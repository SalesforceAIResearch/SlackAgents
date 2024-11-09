from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class FileInput(BaseModel):
    filename: str
    b64_data: str

class CodeRequest(BaseModel):
    code: str
    files: Optional[List[FileInput]] = None

class ErrorResponse(BaseModel):
    type: str
    message: str

class CodeExecutionResponse(BaseModel):
    success: bool
    final_expression: Optional[Any] = None
    output_files: Optional[List[Dict[str, str]]] = None
    error: Optional[ErrorResponse] = None
    std_out: Optional[str] = None
    std_err: Optional[str] = None
    code_runtime: Optional[int] = None
