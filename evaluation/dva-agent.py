import os
import json
import re
import sys
import io
import contextlib
import traceback
import multiprocessing
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm


API_KEYS = [
    "your_api_key"
]


MODEL_NAME = "MODEL_NAME"

TIMEOUT_SECONDS = 300

# 文件路径
INPUT_FILE_PATH = "./OptiVerse-full.json" 

OUTPUT_FILE_PATH = "./OptiVerse_fix.json"


FILE_LOCK = threading.Lock()



def parse_json(content):
    """尝试解析 LLM 返回的 JSON 内容"""
    try:
        content = re.sub(r"//.*", "", content)
        match = re.search(r"```json\s*(.*?)```", content, re.DOTALL)
        if match: 
            json_str = match.group(1).strip()
            return json.loads(json_str)
        
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match: return json.loads(match.group(0))
        return json.loads(content)
    except:
        return {}

def extract_python_code(content):

    match = re.search(r"```python\s*(.*?)```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    if "import " in content or "def " in content:
        return content.strip()
        
    return ""

def _worker_execute(code_str, queue):

    output_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(output_capture):
            exec_globals = {}
            exec(code_str, exec_globals)
        queue.put({"success": True, "output": output_capture.getvalue()})
    except Exception:
        error_msg = traceback.format_exc()
        queue.put({"success": False, "output": error_msg})

def execute_code_locally(code_str):

    if not code_str:
        return False, "No code generated."

    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_worker_execute, args=(code_str, q))
    p.start()
    
    p.join(TIMEOUT_SECONDS)
    
    if p.is_alive():
        p.terminate()
        p.join()
        return False, f"TimeoutError: Execution exceeded {TIMEOUT_SECONDS} seconds."
    
    if not q.empty():
        result = q.get()
        return result['success'], result['output']
    else:
        return False, "RuntimeError: Process finished but returned no result."

def save_data_safe(data, filepath):

    with FILE_LOCK:
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



class SolverAgent:

    def __init__(self, client):
        self.client = client
        self.model = MODEL_NAME

    def run(self, problem_text, expected_keys):
        prompt = f"""
You are an expert in Operations Research and Python Programming.

**Problem Statement**:
{problem_text}

**Goal**: Write a Python script to solve this problem.

**CRITICAL OUTPUT REQUIREMENT**:
The problem has specific required output fields. Your code MUST calculate and explicitly `print()` the computed results for these specific variables/metrics:
[{expected_keys}]

**Guidelines**:
1. **Model First**: Before coding, mentally formulate the mathematical model (Variables, Objectives, Constraints).
2. **Libraries**: Use `scipy`, `pulp`, `ortools`, `numpy`, or `cvxpy`. Choose the best tool for the specific problem (Linear vs Non-Linear).
3. **Structure**: Write a simple, top-level script. **DO NOT** define functions or use `if __name__ == "__main__":`.
4. **Constraint Logic**: Ensure strict adherence to the problem constraints (e.g., integer constraints, non-negativity).
5. **Output**: Use `print()` to output the results formatted as strictly as possible.

**Task:** First, present the modeling logic, then return the Python code enclosed in ```python ... ``` blocks.
    """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = response.choices[0].message.content
            
            # 提取代码
            code_content = extract_python_code(raw_content)
            
            # 提取 Modeling Logic
            if "```python" in raw_content:
                logic_content = raw_content.split("```python")[0].strip()
            else:
                logic_content = raw_content.strip()

            return logic_content, code_content, raw_content
        except Exception as e:
            return f"Error: {str(e)}", "", ""

class HybridDiagnosisAgent:

    def __init__(self, client):
        self.client = client
        self.model = MODEL_NAME

    def run(self, problem_text, current_code, execution_log, success_status, initial_modeling_logic):
        # 1. 运行时错误检查（如果有运行时错误，必须修复）
        if not success_status:
            return self._diagnose_runtime_error(current_code, execution_log)

        # 2. 逻辑审计（如果代码能跑通，检查逻辑是否符合题意）
        logic_errors_text = self._audit_logic_hybrid(problem_text, current_code, execution_log, initial_modeling_logic)
        
        # 如果审计返回 Pass 或空，说明没有严重问题，直接返回空列表
        if not logic_errors_text or logic_errors_text.strip() == "PASS":
            return []
            
        return logic_errors_text

    def _get_response_text(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except:
            return ""

    def _get_response_json(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return parse_json(response.choices[0].message.content)
        except:
            return []


    def _diagnose_runtime_error(self, wrong_code, log):
        prompt = f"""
        Analyze the Python Execution Error.
        Code: {wrong_code}
        Error Log: {log}
        Output: error_category and fix_instruction.
        """
        res = self._get_response_text(prompt)
        return [res]
        # return res.get('errors', [])

    def _audit_logic_hybrid(self, problem_text, code, exec_output, initial_modeling_logic):
        
        # === Step 1: Blind Interpretation (盲测) ===
        phase1_prompt = f"""
        You are a Code Interpreter. 
        Read the Python code below and describe its **Mathematical Logic** in plain English.
        
        **DO NOT** assess if it is correct or incorrect. Just describe what it DOES.
        
        Focus on:
        1. **Objective**: What is being minimized or maximized?
        2. **Variables**: What are the decision variables?
        3. **Constraints**: List the constraints found in the code.
        
        Code:
        ```python
        {code}
        ```
        Output ONLY the mathematical logic description.
        """
        code_logic_desc = self._get_response_text(phase1_prompt)
        if not code_logic_desc: return "PASS" 

        # === Step 2: Requirement Extraction (需求提取 - 增强 PASS 机制) ===
        phase2_prompt = f"""
    Analyze the Optimization Problem and the Reference Modeling Logic.
    
    **Problem Statement**:
    {problem_text}

    **Reference Modeling Logic**:
    {initial_modeling_logic}

    **Task**: 
    Identify any **KEY mathematical requirements** (constraints, specific values, or objective directions) present in the Problem that are **MISSING** in the Reference Modeling Logic.
    
    **Output Instruction**:
    - If the Reference Modeling Logic covers all necessary mathematical aspects effectively, output ONLY the word: **PASS**
    - Otherwise, list the missing requirements concisely.
        """
        specs_str = self._get_response_text(phase2_prompt)
        
 
        if "PASS" in specs_str or "pass" in specs_str.lower().split() or "no missing" in specs_str.lower():
            specs_str = "None (Reference Modeling Logic is complete)."

        # === Step 3: Cross-Reference (三方对账 - 引入裁判机制) ===
        phase3_prompt = f"""
You are a Senior Auditor and Judge.
Compare the following to decide if the current implementation effectively solves the problem.

**A. Problem** (The Ground Truth):
"{problem_text}"

**B. Possible Missing Content** (Analysis from Step 2):
{specs_str}

**C. Current Code Implementation**:
"{code_logic_desc}"

**D. Execution Status**:
Output/Logs: {exec_output}

**Task**: 
Determine if the current modeling logic (C) correctly solves the Problem (A).

**JUDGMENT CRITERIA**:
1. **Equivalent Logic**: If the code uses a mathematically equivalent approach (even if variable names or specific formulations differ from B), treat it as CORRECT.
2. **Analysis B**: If 'B' says "None", it means the initial logic was good. You only need to check if the Code (C) implements it correctly.
3. **Execution**: If the code ran successfully (D) and produced reasonable output, lean towards passing it unless a constraint is clearly violated.

**OUTPUT INSTRUCTION**:
- If the current solution is correct and sufficient, output ONLY the word: **PASS**
- If there are CRITICAL mathematical errors (e.g., wrong objective direction, missing constraints, incorrect formula), describe them clearly.
        """
        res = self._get_response_text(phase3_prompt)
        

        if "PASS" in res or "pass" in res.lower().split():

            if len(res) < 50 or "no critical" in res.lower() or "correct" in res.lower():
                return "PASS"
        
        return res

class RegeneratorAgent:
    """
    修复 Agent
    """
    def __init__(self, client):
        self.client = client
        self.model = MODEL_NAME

    def create_guidelines(self, problem_text, wrong_code, error_list):

        if not error_list or error_list == "PASS":
            return "Pass"
            
        if isinstance(error_list, str):
            raw_issues_text = error_list
        else:
            raw_issues_text = "\n".join([str(e) for e in error_list])
        
        prompt = f"""
You are a Technical Lead.
We attempted to solve a problem and gain some experience.
Problem:
{problem_text}

Experience:
{raw_issues_text}

**Task**: 
You need to consider which of these experiences are applicable and which have some issues.
Then select the appropriate experiences to summarize these issues into a **"Critical Precautions"** for the next developer.
Keep it concise and to the point, no more than five sentences.
Output: ONLY the text of the precautions.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception:
            return raw_issues_text

    def generate_code_two_stage(self, problem_text, initial_modeling_logic, guidelines, expected_keys, previous_execution_error=None, previous_output=None):
        
        # 构造 Context Info
        context_info = f"""
        **⚠️ Critical Precautions from Previous Failures**:
        {guidelines}
        """
        if previous_execution_error:
            context_info += f"\n**Previous Runtime Error**: {previous_execution_error}"
        if previous_output and "Infeasible" in previous_output:
            context_info += "\n**Previous Status**: Infeasible (Check constraints contradictions)."

        # === Step 1: Use existing logic ===
        initial_modeling_text = initial_modeling_logic

        # === Step 2: Review and Refine ===
        step2_prompt = f"""
You are a Senior Technical Reviewer.

We have a **Draft Mathematical Model** for a problem.
However, we also have **Critical Precautions** derived from previous failed attempts.

**Original Problem**:
{problem_text}

**Draft Mathematical Model** (from Initial Attempt):
{initial_modeling_text}

**Critical Precautions & Context**:
{context_info}

**Task**:
1. Review the Draft Model against the Critical Precautions.
2. Please try to modify the mathematical model. Please refer to Critical Precautions & Context.
3. If the Draft Model is fine, optimize it for clarity.

**Output**:
Provide the **FINAL CORRECTED Mathematical Model**.
Only output the full, complete, and corrected modeling logic text.
"""
        try:
            resp_s2 = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": step2_prompt}]
            )
            refined_modeling_text = resp_s2.choices[0].message.content
        except Exception as e:
            refined_modeling_text = initial_modeling_text

        # === Step 3: Coding ===
        step3_prompt = f"""
You are a Python Operations Research Engineer.

**Problem Statement**:
{problem_text}

**Approved Mathematical Model** (Strictly follow this logic):
{refined_modeling_text}

**Goal**: 
Write a Python script to solve this problem based strictly on the Approved Model above.

**Requirements**:
1. **Output**: You MUST calculate and explicitly `print()` the results for these keys: [{expected_keys}].
2. **Libraries**: Use `gurobipy`, `scipy`, `pulp`, `ortools`, `numpy`, or `cvxpy`. Choose the best tool for the specific problem (Linear vs Non-Linear).
3. **Structure**: Write a simple, top-level script. **DO NOT** define functions or use `if __name__ == "__main__":`.
4. **Constraint Logic**: Ensure strict adherence to the problem constraints (e.g., integer constraints, non-negativity).
5. **Format**: Return only the code logic enclosed in ```python ... ```.
6. **Robustness**: Check solver status before printing results.
"""
        try:
            resp_s3 = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": step3_prompt}]
            )
            code_content = extract_python_code(resp_s3.choices[0].message.content)
            return refined_modeling_text, code_content
        except Exception as e:
            return refined_modeling_text, ""

# ================= Thread Worker Function =================

def process_single_task(item, api_key_queue, all_data_ref):
    """单个任务的处理逻辑"""
    api_key = api_key_queue.get()
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # 实例化 Agents
        solver_agent = SolverAgent(client)          
        diagnosis_agent = HybridDiagnosisAgent(client) 
        regenerator_agent = RegeneratorAgent(client)   
        
        question = item.get('question', '')
        expected_keys = list(item.get('results', {}).keys())
        
        if not question: return

        # === Step 1: 初始求解 (Baseline - 单阶段) ===
        initial_logic, code_init, solver_response_raw = solver_agent.run(question, expected_keys)
        success_init, output_init = execute_code_locally(code_init)
        
        # === Step 2: 诊断 ===

        errors = diagnosis_agent.run(question, code_init, output_init, success_init, initial_logic)
        
        final_code = code_init
        final_output = output_init
        final_decision_log = "Initial run accepted (No issues detected)."
        was_repaired = False
        
        code_rep = ""
        output_rep = ""
        modeling_logic_rep = "" 
        success_rep = False
        guidelines_text = ""

        # === Step 3: 尝试修复 (如果 errors 存在，才启用修复) ===
        if errors and errors != "PASS":
            print(f"[Diagnosis] ID {item.get('index')} found issues, attempting repair...")
            guidelines_text = regenerator_agent.create_guidelines(question, code_init, errors)
            
            if guidelines_text.strip().lower() == "pass":
                final_decision_log = "Diagnosis indicated no critical issues (Double Check Passed)."
            else:
                last_exec_error = None 
                last_output = None

                for attempt in range(3):
                    model_text, code_try = regenerator_agent.generate_code_two_stage(
                        question, 
                        initial_logic,
                        guidelines_text, 
                        expected_keys, 
                        previous_execution_error=last_exec_error,
                        previous_output=last_output
                    )
                    
                    if not code_try.strip():
                        final_decision_log = f"Regeneration Attempt {attempt+1} generated empty code."
                        break

                    success_try, output_try = execute_code_locally(code_try)
                    
                    if success_try:
                        code_rep = code_try
                        output_rep = output_try
                        modeling_logic_rep = model_text
                        success_rep = True
                        
                        final_code = code_rep
                        final_output = output_rep
                        was_repaired = True
                        final_decision_log = f"Regeneration succeeded on attempt {attempt+1}."
                        break
                    else:
                        err_snippet = output_try[-800:] if len(output_try) > 800 else output_try
                        last_exec_error = f"Runtime Error found in Attempt {attempt+1}:\n{err_snippet}"
                        last_output = output_try
                        
                        code_rep = code_try
                        output_rep = output_try
                        modeling_logic_rep = model_text
                        final_decision_log = f"Regeneration Attempt {attempt+1} failed."

                if not success_rep and not was_repaired:
                    final_code = code_init
                    final_output = output_init
                    was_repaired = False
                    final_decision_log = "All regeneration attempts failed. Reverted to initial."
        else:

            final_decision_log = "Initial code passed logic audit."

        # === 更新 Item 数据 ===
        item['initial_code'] = code_init
        item['initial_modeling_logic'] = initial_logic
        item['initial_output'] = output_init
        item['initial_success'] = success_init
        item['solver_llm_response'] = solver_response_raw
        
        item['repaired_modeling_logic'] = modeling_logic_rep 
        item['repaired_code_attempt'] = code_rep
        item['repaired_output_attempt'] = output_rep
        item['repaired_success'] = success_rep
        
        item['final_code'] = final_code
        item['final_output'] = final_output
        item['was_repaired'] = was_repaired
        item['selection_logic'] = final_decision_log
        
        item['repair_llm_response'] = guidelines_text 
        item['diagnosis_report'] = errors

        # === 实时保存 ===
        save_data_safe(all_data_ref, OUTPUT_FILE_PATH)

    except Exception as e:
        print(f"Error processing ID {item.get('index')}: {e}")
        traceback.print_exc()
    finally:
        api_key_queue.put(api_key)

# ================= Main Pipeline =================

def main():
    if not API_KEYS:
        print("Error: Please provide at least one API Key in API_KEYS list.")
        return

    # 加载数据
    if os.path.exists(OUTPUT_FILE_PATH):
        print(f"Resuming from: {OUTPUT_FILE_PATH}")
        with open(OUTPUT_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(INPUT_FILE_PATH):
        print(f"Starting fresh from: {INPUT_FILE_PATH}")
        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("Error: No input file found.")
        return

    # 初始化 Key 队列
    key_queue = queue.Queue()
    for key in API_KEYS:
        key_queue.put(key)

    # 筛选未处理的任务
    todo_items = [
        item for item in data 
        if not (item.get('final_code') or item.get('initial_code')) 
    ]
    
    print(f"Total items: {len(data)}")
    print(f"Items to process: {len(todo_items)}")
    
    if not todo_items:
        print("All items processed.")
        return

    num_workers = len(API_KEYS)
    print(f"Starting ThreadPool with {num_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for item in todo_items:
            f = executor.submit(process_single_task, item, key_queue, data)
            futures.append(f)
        
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            pass
            
    print(f"\nAll tasks completed. Results saved to {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    main()