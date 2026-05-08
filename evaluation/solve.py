import os
import json
import time
import re
import sys
import subprocess 
from tqdm import tqdm
import openai


API_KEY = "your_api_key"   
BASE_URL = "base_url"

INPUT_FILE = "./data/OptiVerse-full.json"
OUTPUT_DIR = "./results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Solved.json")


# 模型名称
MODEL_NAME = "MODEL_NAME" 

# 保存间隔
SAVE_INTERVAL = 1

# 请求间隔
SLEEP_TIME = 1 

# 代码执行超时时间 (秒)
EXEC_TIMEOUT = 300
# ===========================================

# 初始化 Client
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

def call_poe_with_retry(prompt, model_name=MODEL_NAME):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response received")
            return content
            
        except Exception as e:
            error_str = str(e)
            print(f"\n[API Error] Attempt {attempt+1}/{max_retries}: {error_str}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return f"Error: API Call Failed - {error_str}"
    
    return "Error: Max retries exceeded."

def extract_code_block(text: str) -> str:
    if not text: return ""

    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match: return match.group(1).strip()

    match_generic = re.search(r"```[a-zA-Z]*\s*(.*?)```", text, re.DOTALL)
    if match_generic: return match_generic.group(1).strip()

    if "import " in text or "def " in text: return text.strip()
    return ""

def execute_python_code(code_str: str, timeout: int = EXEC_TIMEOUT) -> str:

    if not code_str or code_str.startswith("Error"):
        return "No executable code found."

    try:
        result = subprocess.run(
            [sys.executable, "-c", code_str],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout.strip()
        if result.stderr:
            output += f"\n[Stderr]:\n{result.stderr.strip()}"
            
        if not output:
            output = "[Process finished with no output]"
            
        return output

    except subprocess.TimeoutExpired:
        return f"Error: Execution timed out after {timeout} seconds."
    except Exception as e:
        return f"Error: Execution failed - {str(e)}"

def generate_solution_code(question, question_type, standard_results):
    """
    生成解题代码的 Prompt
    """
    expected_keys_str = ", ".join([f'"{k}"' for k in standard_results.keys()]) if standard_results else "Max Profit, Decision Variables"

    prompt = f"""
    You are an expert in Operations Research and Python Programming.
    
    **Problem Statement**:
    {question}
    
    **Goal**: Write a Python script to solve this problem.
    
    **CRITICAL OUTPUT REQUIREMENT**:
    The problem has specific required output fields. Your code MUST calculate and explicitly `print()` the computed results for these specific variables/metrics:
    [{expected_keys_str}]
    
    **Guidelines**:
    1. **Libraries**: You have access to `scipy`, `pulp`, `ortools`, `numpy`, `sympy`, `networkx`, and `cvxpy`. Choose the best tool for the specific problem.
    2. **Performance**: Ensure the code runs within a reasonable time. Keep grid sizes small for numerical methods.
    3. **Output Format**: The code MUST use `print()` statements to clearly output the calculated results associated with the required keys.
    4. **Structure**: Write a simple, top-level script. **DO NOT** define functions or use `if __name__ == "__main__":`.
    5. **Solution**: Solve for the specific numbers or expressions asked in the problem.
    6. **Concise**: The code should be as concise as possible, without any unnecessary comments or explanations.
    
    **Task:** First, present the modeling approach, then return the Python code enclosed in ```python ... ``` blocks.
    """
    
    return call_poe_with_retry(prompt)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    data = []
    if os.path.exists(OUTPUT_FILE):
        print(f"Loading from {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(INPUT_FILE):
        print(f"Loading from {INPUT_FILE}...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("No data found!")
        return

    total_problems = len(data)
    processed_count = 0
    pbar = tqdm(total=total_problems, desc="Generating & Executing")
    for i, item in enumerate(data):
        pbar.update(1)
        if "gemini-2.5flash_code" in item and item["gemini-2.5flash_code"] and not item["gemini-2.5flash_code"].startswith("Error"):
            continue

        index = item.get("index", i)
        pbar.write(f"Processing index {index}...")
        question = item.get("question", "")
        standard_results = item.get("results", {})
        
        if not question: continue
            
        try:
            raw_response = generate_solution_code(question, item.get("type", "Optimization"), standard_results)

            item["gemini-2.5flash_raw_response"] = raw_response

            code = extract_code_block(raw_response)
            
            if not code:
                item["gemini-2.5flash_code"] = "Error: No code generated"
                item["gemini-2.5flash_exec_output"] = "Error: No code to execute"
            else:

                item["gemini-2.5flash_code"] = code

                pbar.write(f"  Executing code for index {index}...")
                exec_output = execute_python_code(code)
                item["gemini-2.5flash_exec_output"] = exec_output
            
            processed_count += 1
            if processed_count % SAVE_INTERVAL == 0:
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            time.sleep(SLEEP_TIME)

        except Exception as e:
            pbar.write(f"Error at index {item.get('index', i)}: {e}")
            item["gemini-2.5flash_code"] = f"Error: Exception - {str(e)}"
            item["gemini-2.5flash_exec_output"] = f"Error: Main Loop Exception - {str(e)}"
            continue

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
