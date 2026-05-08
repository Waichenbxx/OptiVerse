import os
import json
import time
import re
import io
import contextlib
import traceback
import multiprocessing
from tqdm import tqdm
from openai import OpenAI
from collections import defaultdict


DEEPSEEK_API_KEY = "your_api_key" 
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


INPUT_FILE = "./results/Solved.json"
OUTPUT_DIR = "./evaluation"


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Evaluated.json")
STATS_FILE = os.path.join(OUTPUT_DIR, "Stats.json")


SYNTHESIS_MODEL = "deepseek-chat" 
EVAL_MODEL = "deepseek-chat"      


CODE_TIMEOUT = 600

SAVE_INTERVAL = 1 

# ===========================================

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[Warning] Failed to load JSON from {filepath}. Returning empty list.")
            return []
    return []

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Code Execution
def _worker_execute_code(code, result_queue):
    output_buffer = io.StringIO()
    exec_globals = {}
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, exec_globals)
        result_queue.put({"success": True, "output": output_buffer.getvalue()})
    except Exception:
        error_msg = traceback.format_exc()
        result_queue.put({"success": False, "output": f"[Execution Error]:\n{error_msg}"})

def execute_python_code(code: str) -> str:
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=_worker_execute_code, args=(code, queue))
    process.start()
    process.join(CODE_TIMEOUT)
    
    if process.is_alive():
        process.terminate()
        process.join()
        return f"[Execution Error]: Code execution timed out after {CODE_TIMEOUT} seconds."
    
    if not queue.empty():
        result = queue.get()
        output = result.get("output", "")
        if not output.strip() and result.get("success", False):
             return "[System Warning]: Code executed successfully but printed nothing."
        return output
    else:
        return "[Execution Error]: Process finished but returned no output."


# Answer Synthesis
def synthesize_final_answer(question, execution_output, standard_results):
    expected_keys = list(standard_results.keys()) if standard_results else []
    
    prompt = f"""
    You are an intelligent assistant.
    
    **Original Question**:
    {question}
    
    **Execution Output**:
    {execution_output}
    
    **Required JSON Keys**:
    {json.dumps(expected_keys)}
    
    **Task**:
    Extract values from the Execution Output and fill in the JSON keys above.
    - Use "N/A" or "Error" if value is missing.
    - Return ONLY valid JSON.
    
    **Output Format**:
    {{
        "key1": "value1",
        "key2": "value2"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=SYNTHESIS_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'{{"Error": "Synthesis Failed: {str(e)}"}}'


# Evaluation


def check_basic_execution(item):
    answer = item.get("gemini-2.5flash_answer")
    exec_output = item.get("gemini-2.5flash_exec_output", "")
    code = item.get("gemini-2.5flash_code", "")

    if not code or str(code).strip() == "" or str(code).startswith("Error"):
        return False, "No valid code generated"
    
    if not answer:
        return False, "No answer synthesized"
    
    if isinstance(answer, dict) and any("Error" in str(v) for v in answer.values()):
        pass 
    if isinstance(answer, str) and "Error" in answer:
         return False, f"Answer contains error: {answer}"
    
    if not exec_output or "[Execution Error]" in exec_output:
        return False, "Execution failed or timed out"

    return True, "Success"

def evaluate_result_accuracy(question, standard_results, model_answer):
    prompt = f"""
    You are a strict Mathematics and Optimization Teaching Assistant.
    
    **Task**: Comprehensively evaluate whether the "Student's Answer" completely matches the "Standard Solution".
    
    **Context**:
    {question}
    
    **Standard Solution**:
    {json.dumps(standard_results, ensure_ascii=False)}
    
    **Student's Answer**:
    {json.dumps(model_answer, ensure_ascii=False)}
    
    --- EVALUATION CRITERIA (ALL MUST BE MET) ---
    
    1. **Full Scope Matching**: You must check ALL keys/fields present in the Standard Solution. It is NOT enough to just check the objective value.
    2. **Numerical Precision**: For numerical fields, values must match within **0.1%** tolerance. Be strict.
    3. **Unit Conversion**: Handle unit differences intelligently (e.g., 0.5 vs 50%, 5000 vs 5k, 1 vs 100%).
    4. **Strategy/Text Matching**: If a field describes a strategy (e.g., "Strategy: Buy A"), verify if the semantic meaning matches, even if phrasing differs.
    5. **Function/Trajectory Matching**: If a field's answer is a function, control law, or time-dependent trajectory, verify that the mathematical form and structure match (allowing only minor algebraic rephrasing but not substantive changes).

    **Verdict Logic**:
    - Return `is_correct: true` ONLY if ALL standard fields are accurately represented in the student's answer.
    - If ANY key is missing, numerically off (>0.1%), or logically incorrect, return `false`.

    **Output Format (STRICT)**:
    Provide reasoning first.
    ```json
    {{
        "reason": "Step 1: Check Objective Value... Step 2: Check Decision Variables... Step 3: Check Strategy... Conclusion...",
        "is_correct": true  // or false (Output this AFTER reasoning)
    }}
    ```
    """
    
    try:
        response = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": "You are a JSON generator. output reasoning first."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"is_correct": False, "reason": f"LLM API Error: {str(e)}"}

def calculate_statistics(data):
    stats = {
        "Overall": {"total": 0, "exec_success": 0, "result_acc_pass": 0, "solved": 0},
        "Category_L1": defaultdict(lambda: {"total": 0, "solved": 0}),
    }

    for item in data:
        if "tri_eval" not in item: 
            continue
            
        res = item["tri_eval"]
        l1 = item.get("category_lvl1", "Unknown")
        
        stats["Overall"]["total"] += 1
        stats["Category_L1"][l1]["total"] += 1
        
        if res.get("exec_success"): stats["Overall"]["exec_success"] += 1
        if res.get("result_pass"): stats["Overall"]["result_acc_pass"] += 1
            
        if (res.get("exec_success") and res.get("result_pass")):
            stats["Overall"]["solved"] += 1
            stats["Category_L1"][l1]["solved"] += 1

    def fmt_pct(num, total):
        return f"{(num/total*100):.2f}%" if total > 0 else "0.00%"

    return {
        "Total Valid Problems": stats["Overall"]["total"],
        "Metrics": {
            "1. Execution Success Rate": fmt_pct(stats["Overall"]["exec_success"], stats["Overall"]["total"]),
            "2. Result Accuracy Rate": fmt_pct(stats["Overall"]["result_acc_pass"], stats["Overall"]["total"]),
            "★ Solved Rate": fmt_pct(stats["Overall"]["solved"], stats["Overall"]["total"])
        },
        "By_Category": {k: fmt_pct(v["solved"], v["total"]) for k, v in stats["Category_L1"].items()}
    }


def main():
    multiprocessing.freeze_support() 


    print(f"Loading Source Input: {INPUT_FILE}")
    input_data = load_json(INPUT_FILE)
    if not input_data:
        print("Error: Source input file is empty or not found.")
        return


    progress_map = {}
    if os.path.exists(OUTPUT_FILE):
        print(f"Loading Existing Progress: {OUTPUT_FILE}")
        existing_data = load_json(OUTPUT_FILE)

        for item in existing_data:
            idx = item.get("index")
            if idx is not None:
                progress_map[idx] = item
        print(f"  -> Found {len(progress_map)} items in progress file.")


    merged_data = []
    
    KEY_CODE = "gemini-2.5flash_code"
    KEY_ANS = "gemini-2.5flash_answer"

    print("Merging data based on 'index'...")
    for item in input_data:
        idx = item.get("index")
        

        if idx is not None and idx in progress_map:
            final_item = progress_map[idx]
        else:
            final_item = item 
        

        code_content = final_item.get(KEY_CODE)
        answer_content = final_item.get(KEY_ANS)
        
        has_code = code_content is not None and str(code_content).strip() != ""
        has_answer = answer_content is not None and str(answer_content).strip() != ""
        
        if has_code or has_answer:
            merged_data.append(final_item)

    data = merged_data
    print(f"Total merged & filtered items to process: {len(data)}")


    pbar = tqdm(total=len(data), desc="Processing")
    processed_count = 0
    save_trigger = False

    KEY_EVAL = "tri_eval"
    KEY_EXEC = "gemini-2.5flash_exec_output"

    for i, item in enumerate(data):
        pbar.update(1)
        save_trigger = False
        
        code_content = item.get(KEY_CODE)
        has_ans = KEY_ANS in item
        has_eval = KEY_EVAL in item


        if has_ans and has_eval:
            continue


        if not has_ans:
            if code_content and str(code_content).strip() != "":
                current_exec = item.get(KEY_EXEC, "")
                if not current_exec:
                    exec_output = execute_python_code(code_content)
                    item[KEY_EXEC] = exec_output
                    current_exec = exec_output
                    save_trigger = True

                if current_exec and not current_exec.startswith("[Execution Error]"):
                    question = item.get("question", "")
                    std_results = item.get("results", {})
                    ans_str = synthesize_final_answer(question, current_exec, std_results)
                    try:
                        item[KEY_ANS] = json.loads(ans_str)
                    except:
                        item[KEY_ANS] = f"Error parsing JSON: {ans_str}"
                    has_ans = True 
                    save_trigger = True
                else:
                    save_trigger = True


        if not has_eval:
            
            eval_res = {
                "exec_success": False,
                "result_pass": False,
                "result_reason": ""
            }

            is_exec_ok, exec_msg = check_basic_execution(item)
            eval_res["exec_success"] = is_exec_ok
            eval_res["exec_reason"] = exec_msg

            std_res = item.get("results", {})
            model_ans = item.get(KEY_ANS, {})
            
            if is_exec_ok and std_res:
                r1 = evaluate_result_accuracy(item.get("question"), std_res, model_ans)
                eval_res["result_pass"] = r1.get("is_correct", False)
                eval_res["result_reason"] = r1.get("reason", "N/A")
            elif not std_res:
                eval_res["result_reason"] = "Skipped: No Standard Solution"
            else:
                eval_res["result_reason"] = "Skipped: Execution/Synthesis Failed"
            
            item[KEY_EVAL] = eval_res
            save_trigger = True


        if save_trigger:
            processed_count += 1
            if processed_count % SAVE_INTERVAL == 0:
                save_json(data, OUTPUT_FILE)

    save_json(data, OUTPUT_FILE)
    
    print("\nCalculating Statistics (Valid problems only)...")
    report = calculate_statistics(data)
    save_json(report, STATS_FILE)
    
    print("\n" + "="*40)
    print("🏆 FINAL REPORT")
    print("="*40)
    print(json.dumps(report["Metrics"], indent=2))
    print(f"\nSaved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
