r"""
SlackAgents Code Interpreter Service
====================================

A secure Python code execution service that provides a sandboxed environment for running
user-submitted code snippets. Built with FastAPI, this service is an integral
part of the SlackAgents platform.

Features:
---------
* Secure code execution in an isolated environment
* File handling support
* API key authentication
* Comprehensive error handling

Endpoints:
----------
* POST /submit: Execute Python code in sandbox
* GET  /health: Service health check

Authentication:
--------------
All requests (except /health) require an API key provided via the 'authorization' header.

Dependencies:
------------
* FastAPI: Web framework
* Python 3.8+
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from logging.handlers import RotatingFileHandler
from environment import PythonEnvironment
from schemas import CodeRequest, CodeExecutionResponse
from dotenv import load_dotenv, find_dotenv
import logging
load_dotenv(find_dotenv())

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SlackAgents Code Interpreter Service", 
    description="Executes Python code in a containerized Python sandbox environment and returns the output"
)

# Add API key security scheme with key name "authorization" in header
API_KEY_NAME = "authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    return api_key

async def verify_api_key(api_key: str = Depends(get_api_key)):
    sandbox_api_key = os.getenv("SANDBOX_API_KEY")
    if not sandbox_api_key:
        return None  # Skip authentication if SANDBOX_API_KEY is not set
    if api_key != sandbox_api_key:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False, 
                "error": {"type": "auth", "message": "Invalid API key"}
            }
        )
    return api_key

# Global environment instance
python_env = PythonEnvironment()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    await python_env.prepare_environment()
    await python_env.load_environment()
    logger.info("Environment loaded successfully")

@app.post("/submit", response_model=CodeExecutionResponse, dependencies=[Depends(verify_api_key)])
async def execute_code(request: CodeRequest):
    if not request.code or request.code.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={
                "success": False, 
                "error": {"type": "parsing", "message": "no code provided"}
            }
        )
    
    result = await python_env.run_code(request.code, request.files or [])
    
    # Cleanup after response is prepared
    await python_env.cleanup()
    await python_env.terminate()
    
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser(description="Run the SlackAgents Code Interpreter Service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the service on")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the service on")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)