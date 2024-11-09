import requests
import base64
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

SANDBOX_URL = os.getenv("SANDBOX_URL")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR")

files: List[Dict] = []
# Dictionary to map filenames to their b64_data
file_map: Dict[str, str] = {}
# Each file is a dictionary with the following keys:
# - "filename": The name of the file
# - "b64_data": The base64 encoded data of the file

def code_interpreter(code: str) -> str:
    """Executes Python code on the user's machine **in the users environment**, returns the output and keeps the output files in the users environment. You can only execute the code in previously generated code. Do not generate code here.
    
    :param code: The Python code to execute. To show tool execution results, the code MUST use print() in the code instread of return, or explicitly save the results to a file in the code. 
    :type code: string
    :return: The results of the code execution.
    :rtype: string
    """
    # Preprocess the code
    code = code.replace("```python", "").replace("```", "").strip()
    try:
        response = requests.post(
            f"{SANDBOX_URL}/submit", 
            json={"code": code, "files": files}
        )
        output = response.json()
        if not output["success"]:
            return output["std_err"]
        else:
            std_output = output["std_out"]
            output_files = output["output_files"]
            for file in output_files:
                with open(f"{WORKSPACE_DIR}/{file['filename']}", "wb") as f:
                    f.write(base64.b64decode(file["b64_data"]))
                files.append({
                    "filename": file["filename"],
                    "b64_data": file["b64_data"]
                })
                file_map[file['filename']] = file['b64_data']
            return std_output
    except Exception as e:
        return str(e)
