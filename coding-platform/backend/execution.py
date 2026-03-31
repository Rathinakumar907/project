import subprocess
import os
import uuid
import time
import re
import shutil
from typing import Dict, Any, Optional, List

# Docker Sandbox Configuration
DOCKER_IMAGES = {
    "python": "python:3.10-alpine",
    "c": "gcc:latest",
    "cpp": "gcc:latest",
    "java": "openjdk:17-alpine"
}

# DELIMITERS for strict output extraction
START_MARKER = "---BEGIN_SOLUTION_OUTPUT---"
END_MARKER = "---END_SOLUTION_OUTPUT---"

def wrap_python_code(code: str) -> str:
    """
    Wraps student code in a hidden driver to capture strict output 
    and prevent global scope pollution.
    """
    # Escaping triple quotes in student code to prevent breaking the driver
    escaped_code = code.replace('"""', '\"\"\"').replace("'''", "\'\'\'")
    
    driver = f"""
import sys
import io

# Delimiters
START = "{START_MARKER}"
END = "{END_MARKER}"

def __hidden_solution__():
    # Student Code Starts Here
{re.sub('^', '    ', code, flags=re.MULTILINE)}
    # Student Code Ends Here

if __name__ == "__main__":
    # Redirect stdout to capture exact output
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        __hidden_solution__()
        sys.stdout = original_stdout
        print(START)
        print(captured_output.getvalue(), end='')
        print(END)
    except Exception as e:
        sys.stdout = original_stdout
        print(f"Runtime Error: {{e}}", file=sys.stderr)
        sys.exit(1)
"""
    return driver

def run_code_in_sandbox(code: str, language: str, input_data: str, timeout_seconds: int = 2) -> Dict[str, Any]:
    """
    Runs code inside a Docker container with restricted resources and no network.
    """
    run_id = str(uuid.uuid4())
    work_dir = os.path.abspath(f"./temp_runs/{run_id}")
    os.makedirs(work_dir, exist_ok=True)
    
    # Language specific setup
    ext_map = {"python": ".py", "c": ".c", "cpp": ".cpp", "java": ".java"}
    file_name = f"solution{ext_map.get(language, '.txt')}"
    file_path = os.path.join(work_dir, file_name)
    
    if language == "python":
        wrapped_code = wrap_python_code(code)
    else:
        wrapped_code = code

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(wrapped_code)

    result_dict = {
        "status": "Accepted",
        "output": "",
        "execution_time": 0
    }

    image = DOCKER_IMAGES.get(language)
    if not image:
        return {"status": "Server Error", "output": "Unsupported language", "execution_time": 0}

    # Attempt Docker execution first
    try:
        docker_cmd = [
            "docker", "run", "--rm", "-i",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "--volume", f"{work_dir}:/code:ro",
            "--workdir", "/code",
            image
        ]

        if language == "python":
            docker_cmd += ["python", file_name]
        elif language == "c":
            docker_cmd += ["sh", "-c", f"gcc -o sol {file_name} && ./sol"]
        elif language == "cpp":
            docker_cmd += ["sh", "-c", f"g++ -o sol {file_name} && ./sol"]
        elif language == "java":
            docker_cmd += ["sh", "-c", f"javac {file_name} && java solution"]

        start_time = time.time()
        process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=input_data, timeout=timeout_seconds)
        end_time = time.time()
        
    except (FileNotFoundError, subprocess.CalledProcessError, Exception) as e:
        # FALLBACK: Local Execution if Docker is missing or fails
        # Warning: This is less secure but allows the platform to function
        start_time = time.time()
        try:
            if language == "python":
                local_cmd = ["python", file_path]
            elif language == "c" and os.name == "nt":
                # Very basic GCC check for Windows
                subprocess.run(["gcc", "-o", os.path.join(work_dir, "sol.exe"), file_path], capture_output=True)
                local_cmd = [os.path.join(work_dir, "sol.exe")]
            else:
                return {"status": "Server Error", "output": f"Docker missing and local fallback failed for {language}", "execution_time": 0}

            process = subprocess.Popen(
                local_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=work_dir
            )
            stdout, stderr = process.communicate(input=input_data, timeout=timeout_seconds)
            end_time = time.time()
        except Exception as local_e:
            return {"status": "Server Error", "output": f"Sandbox failed and local fallback error: {str(local_e)}", "execution_time": 0}
        
        exec_time_ms = int((end_time - start_time) * 1000)
        result_dict["execution_time"] = exec_time_ms

        if process.returncode != 0:
            result_dict["status"] = "Runtime Error" if process.returncode != 124 else "Time Limit Exceeded"
            result_dict["output"] = stderr.strip() or stdout.strip()
        else:
            # Extract output between markers for Python
            if language == "python" and START_MARKER in stdout:
                pattern = f"{START_MARKER}\\s*(.*?)\\s*{END_MARKER}"
                match = re.search(pattern, stdout, re.DOTALL)
                if match:
                    full_output = match.group(1).strip()
                    # To "Ignore extra prints", we take only the last non-empty line
                    lines = [l.strip() for l in full_output.split('\n') if l.strip()]
                    result_dict["output"] = lines[-1] if lines else ""
                else:
                    result_dict["output"] = stdout.strip()
            else:
                result_dict["output"] = stdout.strip()

    except subprocess.TimeoutExpired:
        # Docker handles its own timeout usually if we wrap it, 
        # but the subprocess call also needs a timeout.
        subprocess.run(["docker", "kill", run_id], capture_output=True) # Attempt to kill if it had a name
        result_dict["status"] = "Time Limit Exceeded"
        result_dict["output"] = ""
    except Exception as e:
        result_dict["status"] = "Server Error"
        result_dict["output"] = str(e)
    finally:
        # Cleanup
        try:
            shutil.rmtree(work_dir)
        except:
            pass
            
    return result_dict

def evaluate_submission(code: str, language: str, testcases: list, total_marks: int = 100, reference_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluates submission against testcases using the secure sandbox.
    Distinguishes between Sample and Hidden testcases based on weight.
    """
    total_tc = len(testcases)
    if total_tc == 0:
        return {"result": "No Test Cases", "score": 0, "passed_testcases": 0, "total_testcases": 0}

    # Identify Sample vs Hidden
    # Convention: marks_weight == 0 is SAMPLE, > 0 is HIDDEN
    sample_tcs = [tc for tc in testcases if getattr(tc, 'marks_weight', 1) == 0]
    hidden_tcs = [tc for tc in testcases if getattr(tc, 'marks_weight', 1) > 0]
    
<<<<<<< HEAD
    from .grading.utils import compare_output
    
    for idx, tc in enumerate(testcases):
        res = run_code_locally(code, language, tc.input_data)
=======
    # If all have weight > 0, treat the first one as sample for visual feedback
    if not sample_tcs and testcases:
        sample_tcs = [testcases[0]]
        hidden_tcs = testcases[1:]

    passed_hidden = 0
    total_hidden_weight = sum(tc.marks_weight for tc in hidden_tcs) or 1
    passed_hidden_weight = 0
    
    max_time = 0
    first_failure = None

    # Step 1: Run Sample Test Cases (Feedback allowed)
    samples_passed = 0
    for idx, tc in enumerate(sample_tcs):
        res = run_code_in_sandbox(code, language, tc.input_data)
>>>>>>> aa74a66596cc9d04f769d430af651f8acd3ae11c
        max_time = max(max_time, res["execution_time"])
        
        actual = res["output"].strip().replace('\r\n', '\n')
        expected = tc.expected_output.strip().replace('\r\n', '\n')
        
<<<<<<< HEAD
        if res["status"] == "Accepted":
            actual_output = res["output"]
            expected_out = tc.expected_output
            
            if compare_output(expected_out, actual_output):
                passed_tc += 1
                passed_weight += weight
            else:
                if not first_failure:
                    act_short = actual_output.strip()[:50].replace('\n', ' ')
                    exp_short = expected_out.strip()[:50].replace('\n', ' ')
                    first_failure = {
                        "result": "Wrong Answer",
                        "failed_testcase": idx + 1,
                        "error_details": f"Expected: {exp_short}... Got: {act_short}..."
                    }
=======
        if res["status"] == "Accepted" and actual == expected:
            samples_passed += 1
>>>>>>> aa74a66596cc9d04f769d430af651f8acd3ae11c
        else:
            if not first_failure:
                first_failure = {
                    "result": res["status"] if res["status"] != "Accepted" else "Wrong Answer",
                    "failed_testcase": idx + 1,
                    "error_details": f"Sample Failed. Expected: {expected[:100]} Got: {actual[:100]}"
                }
<<<<<<< HEAD
                
    # Strict Per-Question Grading Logic
    ratio = (passed_weight / total_weight) if total_weight > 0 else 0
    
    if ratio == 1.0 and total_tc > 0:
        score = total_marks
        result_status = "Accepted"
        error_details = ""
    elif ratio >= 0.8:
        score = int(total_marks * 0.80)
        result_status = "Partially Correct"
        error_details = "Logic is correct but code is incomplete."
    elif ratio >= 0.5:
        score = int(total_marks * 0.60)
        result_status = "Partially Correct"
        error_details = "Code or theoretical answer is partially correct."
    elif ratio > 0:
        score = int(total_marks * 0.40)
        result_status = "Partially Correct"
        error_details = "Answer is minimally correct."
    else:
        score = int(total_marks * 0.15)
        result_status = "Wrong Answer"
        error_details = "No valid logic is present."
=======

    # Step 2: Run Hidden Test Cases (Feedback restricted)
    for idx, tc in enumerate(hidden_tcs):
        res = run_code_in_sandbox(code, language, tc.input_data)
        max_time = max(max_time, res["execution_time"])
        
        actual = res["output"].strip().replace('\r\n', '\n')
        expected = tc.expected_output.strip().replace('\r\n', '\n')
        
        if res["status"] == "Accepted" and actual == expected:
            passed_hidden += 1
            passed_hidden_weight += tc.marks_weight
        else:
            if not first_failure:
                # MASK FAILURE DETAILS for Hidden Test Cases
                first_failure = {
                    "result": res["status"] if res["status"] != "Accepted" else "Wrong Answer",
                    "failed_testcase": len(sample_tcs) + idx + 1,
                    "error_details": "Hidden test case failed. All inputs and outputs are hidden for security."
                }

    # Final Score based ONLY on hidden test cases
    score = int((passed_hidden_weight / total_hidden_weight) * total_marks)
    
    # Overall Status
    total_passed = samples_passed + passed_hidden
    if total_passed == total_tc:
        result_status = "Accepted"
    elif total_passed > 0:
        result_status = "Partially Correct"
    else:
        result_status = first_failure["result"] if first_failure else "Wrong Answer"
>>>>>>> aa74a66596cc9d04f769d430af651f8acd3ae11c

    return {
        "result": result_status,
        "score": score,
        "execution_time": f"{max_time}ms",
        "passed_testcases": total_passed,
        "total_testcases": total_tc,
        "failed_testcase": first_failure["failed_testcase"] if first_failure else None,
        "error_details": error_details + ("\n" + first_failure["error_details"] if first_failure else "")
    }
