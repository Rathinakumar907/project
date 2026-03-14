import subprocess
import os
import uuid
import time
from typing import Dict, Any, Optional

# Local execution fallback (no docker)
LANGUAGE_CONFIG = {
    "python": {
        "ext": ".py",
        "command": "python"
    },
    "c": {
        "ext": ".c",
        "compile": "gcc -o solution {file}",
        "command": "solution"
    },
    "cpp": {
        "ext": ".cpp",
        "compile": "g++ -o solution {file}",
        "command": "solution"
    },
    "java": {
        "ext": ".java",
        "compile": "javac {file}",
        "command": "java Solution"
    }
}

def run_code_locally(code: str, language: str, input_data: str, timeout_seconds: int = 5) -> Dict[str, Any]:
    if language not in LANGUAGE_CONFIG:
        return {"status": "Runtime Error", "output": "Unsupported language", "execution_time": 0}

    config = LANGUAGE_CONFIG[language]
    run_id = str(uuid.uuid4())
    work_dir = os.path.abspath(f"./temp_runs/{run_id}")
    os.makedirs(work_dir, exist_ok=True)
    
    file_name = f"Solution{config['ext']}"
    file_path = os.path.join(work_dir, file_name)
    
    # Suppress input prompts for Python to prevent Wrong Answer grading failures
    if language == "python":
        override = (
            "import builtins\n"
            "builtins._original_input = getattr(builtins, 'input', input)\n"
            "def _custom_input(prompt=''):\n"
            "    return builtins._original_input()\n"
            "builtins.input = _custom_input\n"
        )
        code = override + code

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    result_dict = {
        "status": "Accepted",
        "output": "",
        "execution_time": 0
    }
    
    try:
        if "compile" in config:
            compile_cmd = config["compile"].format(file=file_name).split()
            compile_proc = subprocess.run(compile_cmd, cwd=work_dir, capture_output=True, text=True)
            if compile_proc.returncode != 0:
                result_dict["status"] = "Compilation Error"
                result_dict["output"] = compile_proc.stderr
                return result_dict
                
            run_cmd = config["command"].split()
            if language in ["c", "cpp"] and os.name == "nt":
                run_cmd[0] += ".exe" # Windows executable
        else:
            run_cmd = [config["command"], file_name]
            
        start_time = time.time()
        
        process = subprocess.Popen(
            run_cmd,
            cwd=work_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if input_data and not input_data.endswith('\n'):
            input_data += '\n'
            
        stdout, stderr = process.communicate(input=input_data, timeout=timeout_seconds)
        end_time = time.time()
        
        exec_time_ms = int((end_time - start_time) * 1000)
        result_dict["execution_time"] = exec_time_ms
        
        if process.returncode != 0:
            result_dict["status"] = "Runtime Error"
            result_dict["output"] = stderr.strip() if stderr else stdout.strip()
        else:
            result_dict["output"] = stdout.strip()

    except subprocess.TimeoutExpired:
        if 'process' in locals():
            process.kill()
        result_dict["status"] = "Time Limit Exceeded"
        result_dict["output"] = ""
    except Exception as e:
        result_dict["status"] = "Server Error"
        result_dict["output"] = str(e)
    finally:
        # Cleanup temp directory
        try:
            os.remove(file_path)
            if os.path.exists(os.path.join(work_dir, "solution.exe")):
                os.remove(os.path.join(work_dir, "solution.exe"))
            if os.path.exists(os.path.join(work_dir, "Solution.class")):
                os.remove(os.path.join(work_dir, "Solution.class"))
            os.rmdir(work_dir)
        except Exception:
            pass
            
    return result_dict

from .grading.partial_grader import PartialGrader

def evaluate_submission(code: str, language: str, testcases: list, total_marks: int = 100, reference_code: Optional[str] = None) -> Dict[str, Any]:
    max_time = 0
    
    # If Python and reference code is provided, use partial grader
    if language == "python" and reference_code:
        formatted_testcases = [{"input": tc.input_data, "expected": tc.expected_output, "weight": getattr(tc, 'marks_weight', 1)} for tc in testcases]
        partial_res = PartialGrader.grade(code, reference_code, formatted_testcases, total_marks)

        total_tc = len(formatted_testcases)
        score = partial_res["score"]
        # Estimate passed test cases from score percentage
        passed_tc = round((score / 100) * total_tc) if total_tc > 0 else 0

        error_msg = partial_res["message"]
        if partial_res.get("syntax_error") and partial_res.get("syntax_error_details"):
            error_msg += "\n" + str(partial_res["syntax_error_details"])

        return {
            "result": partial_res["status"].title(),
            "execution_time": "0ms",
            "score": score,
            "passed_testcases": passed_tc,
            "total_testcases": total_tc,
            "failed_testcase": None if partial_res["status"] == "accepted" else 1,
            "error_details": error_msg,
        }

    # Fallback/Other languages (Run ALL test cases)
    passed_tc = 0
    total_tc = len(testcases)
    total_weight = sum(getattr(tc, 'marks_weight', 1) for tc in testcases) or 1
    passed_weight = 0
    first_failure = None
    
    for idx, tc in enumerate(testcases):
        res = run_code_locally(code, language, tc.input_data)
        max_time = max(max_time, res["execution_time"])
        
        weight = getattr(tc, 'marks_weight', 1)
        
        if res["status"] == "Accepted":
            actual_output = res["output"].strip().replace('\r\n', '\n')
            expected_out = tc.expected_output.strip().replace('\r\n', '\n')
            
            if actual_output == expected_out:
                passed_tc += 1
                passed_weight += weight
            else:
                if not first_failure:
                    first_failure = {
                        "result": "Wrong Answer",
                        "failed_testcase": idx + 1,
                        "error_details": f"Expected: {expected_out[:50]}... Got: {actual_output[:50]}..."
                    }
        else:
            if not first_failure:
                first_failure = {
                    "result": res["status"],
                    "failed_testcase": idx + 1,
                    "error_details": res["output"][:200]
                }
                
    # Calculate score: (passed_weight / total_weight) * total_marks
    score = int((passed_weight / total_weight) * total_marks)
    
    result_status = "Accepted" if passed_tc == total_tc else ( "Partially Correct" if passed_tc > 0 else (first_failure["result"] if first_failure else "Wrong Answer") )

    return {
        "result": result_status,
        "score": score,
        "execution_time": f"{max_time}ms",
        "passed_testcases": passed_tc,
        "total_testcases": total_tc,
        "failed_testcase": first_failure["failed_testcase"] if first_failure else None,
        "error_details": first_failure["error_details"] if first_failure else ""
    }
