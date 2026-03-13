import subprocess
import os
import time
import signal
from typing import Dict, Any, Optional

class SandboxExecutor:
    @staticmethod
    def run_code(
        code: str, 
        input_data: str = "", 
        timeout: float = 2.0, 
        memory_limit_mb: int = 128
    ) -> Dict[str, Any]:
        """
        Runs Python code in a restricted subprocess.
        Note: True memory limiting/sandboxing is easier on Linux (cgroups/Namespaces).
        On Windows, we use basic subprocess management.
        """
        # Create a temp file for the code
        import uuid
        run_id = str(uuid.uuid4())
        temp_dir = os.path.join(os.getcwd(), "temp_runs")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{run_id}.py")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = {
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "timed_out": False,
            "duration": 0.0
        }

        start_time = time.time()
        try:
            # Use a restricted environment if possible
            env = os.environ.copy()
            # Minimal safety: Remove some sensitive env vars
            for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "DATABASE_URL"]:
                if key in env:
                    del env[key]

            process = subprocess.Popen(
                ["python", file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1
            )

            try:
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                result["stdout"] = stdout
                result["stderr"] = stderr
                result["exit_code"] = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result["stdout"] = stdout
                result["stderr"] = stderr
                result["timed_out"] = True
                result["exit_code"] = -1
        
        except Exception as e:
            result["stderr"] = str(e)
            result["exit_code"] = -1
        finally:
            result["duration"] = time.time() - start_time
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

        return result
