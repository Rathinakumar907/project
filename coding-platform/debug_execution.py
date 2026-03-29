import subprocess
import os
import io

code = """
data = input("")
print(data)
"""

driver = f"""
import sys
import io

def __hidden_solution__():
{chr(10).join('    ' + line for line in code.strip().split(chr(10)))}

if __name__ == "__main__":
    captured_output = io.StringIO()
    # sys.stdout = captured_output # Commenting this out to see what happens
    try:
        __hidden_solution__()
        print("RESULT:" + captured_output.getvalue().strip())
    except Exception as e:
        print(f"Runtime Error: {{e}}", file=sys.stderr)
        sys.exit(1)
"""

with open("test_sol.py", "w") as f:
    f.write(driver)

try:
    process = subprocess.Popen(
        ["python", "test_sol.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input="Hello World", timeout=2)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    print("RETURN CODE:", process.returncode)
except Exception as e:
    print("ERROR:", e)

os.remove("test_sol.py")
