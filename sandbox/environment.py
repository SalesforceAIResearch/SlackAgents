import logging
import base64
import time
import os
import sys
import venv
import subprocess
from pathlib import Path
from typing import List, Set
from schemas import FileInput, CodeExecutionResponse, ErrorResponse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

PACKAGE_LIST = [package.strip() for package in os.getenv("PACKAGE_LIST", "").split(",")]

class PythonEnvironment:
    VENV_PATH = "python_sandbox"
    PYTHON_HOME = Path(VENV_PATH) / "workspace"

    def __init__(self):
        self.venv_python = None
        self.out_string = ""
        self.err_string = ""
        self.default_files = []
        self.default_file_names: Set[str] = set()
        self.process = None

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Python Environment")

    async def prepare_environment(self):
        """Load default files and set up virtual environment"""
        self.logger.info("Preparing venv environment")
        
        # Create virtual environment if it doesn't exist
        if not Path(self.VENV_PATH).exists():
            self.logger.info(f"Creating new virtual environment at {self.VENV_PATH}")
            venv.create(self.VENV_PATH, with_pip=True, clear=True)
            self.venv_python = Path(self.VENV_PATH) / "bin" / "python"
            # Ensure pip is installed and updated
            self.logger.info("Ensuring pip is installed and up to date")
            try:
                subprocess.run([
                    str(self.venv_python), "-m", "ensurepip", "--upgrade"
                ], check=True, capture_output=True, text=True)
                
                subprocess.run([
                    str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to setup pip: {e.stderr}")
                raise
            
        # Set python interpreter path
        if sys.platform == "win32":
            self.venv_python = Path(self.VENV_PATH) / "Scripts" / "python.exe"
            self.logger.debug(f"Windows platform detected, python path: {self.venv_python}")
        else:
            self.venv_python = Path(self.VENV_PATH) / "bin" / "python"
            self.logger.debug(f"Unix platform detected, python path: {self.venv_python}")

        # Create workspace directory
        self.logger.info(f"Creating workspace directory at {self.PYTHON_HOME}")
        self.PYTHON_HOME.mkdir(parents=True, exist_ok=True)

        # Load default files if they exist
        default_dir = Path("default_python_home")
        if not default_dir.exists():
            self.logger.warning("Default directory not found at default_python_home")
            return
            
        self.logger.info("Loading default files")
        for file_path in default_dir.glob("*"):
            if file_path.is_file():
                self.logger.debug(f"Loading default file: {file_path}")
                with open(file_path, "rb") as f:
                    data = f.read()
                filename = file_path.name
                self.default_files.append({
                    "filename": filename,
                    "byte_data": bytearray(data)
                })
                self.default_file_names.add(filename)
        self.logger.info(f"Loaded {len(self.default_files)} default files")

    async def load_environment(self):
        """Initialize Python environment with default configuration"""
        self.logger.info("Loading Python environment")
        self.out_string = ""
        self.err_string = ""

        # Install required packages
        self.logger.info(f"Installing required packages: {PACKAGE_LIST}")
        result = subprocess.run([
            str(self.venv_python), "-m", "pip", "install",
            *PACKAGE_LIST
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Package installation failed: {result.stderr}")
        else:
            self.logger.debug(f"Package installation output: {result.stdout}")

        # Write default files to workspace
        self.logger.info("Writing default files to workspace")
        for f in self.default_files:
            file_path = self.PYTHON_HOME / f['filename']
            self.logger.debug(f"Writing file: {file_path}")
            file_path.write_bytes(f['byte_data'])

        self.logger.info("Python environment is loaded with packages installed")

    def list_files_recursive(self, dir_path: str) -> List[str]:
        """Recursively list files in workspace"""
        self.logger.debug(f"Listing files recursively in {dir_path}")
        files = []
        dir_path = Path(dir_path)
        
        for entry in dir_path.rglob("*"):
            if entry.is_file():
                if entry.name not in self.default_file_names:
                    files.append(str(entry))
                    self.logger.debug(f"Found file: {entry}")
        
        self.logger.debug(f"Found {len(files)} non-default files")
        return files

    async def run_code(self, code: str, files: List[FileInput]) -> CodeExecutionResponse:
        self.logger.info("Starting code execution")
        start_time = time.time()
        result = CodeExecutionResponse(success=True)

        try:
            # Write input files
            self.logger.info(f"Processing {len(files)} input files")
            for f in files:
                if not f.filename or not f.b64_data:
                    self.logger.error(f"Invalid file data: {f}")
                    return CodeExecutionResponse(
                        success=False,
                        error=ErrorResponse(
                            type="parsing",
                            message=f"file data is missing for: {f}"
                        )
                    )
                
                file_path = self.PYTHON_HOME / f.filename
                self.logger.debug(f"Writing input file: {file_path}")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(self.base64_to_bytes(f.b64_data))

            # Write code to temporary file
            code_file = self.PYTHON_HOME / "_temp_code.py"
            self.logger.debug(f"Writing code to temporary file: {code_file}")
            code_file.write_text(code)

            # Execute code in virtual environment with working directory set to PYTHON_HOME
            self.logger.info("Executing code in virtual environment")
            process = subprocess.Popen(
                [str(self.venv_python.absolute()), str(code_file.absolute())],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.PYTHON_HOME)
            )
            
            stdout, stderr = process.communicate()
            self.out_string = stdout
            self.err_string = stderr

            if process.returncode != 0:
                self.logger.warning(f"Code execution returned non-zero exit code: {process.returncode}")
                self.logger.debug(f"stderr: {stderr}")
            else:
                self.logger.debug(f"Code execution successful, stdout: {stdout}")

            # Collect output files
            self.logger.info("Collecting output files")
            all_files = self.list_files_recursive(str(self.PYTHON_HOME))
            input_file_names = {f.filename for f in files}
            
            new_files = []
            for f in all_files:
                # Skip temporary code file using exact filename match
                if Path(f).name == "_temp_code.py":
                    continue
                rel_path = Path(f).relative_to(self.PYTHON_HOME)
                if str(rel_path) not in input_file_names:
                    self.logger.debug(f"Processing output file: {rel_path}")
                    new_files.append({
                        "filename": str(rel_path),
                        "b64_data": self.read_file_as_base64(f)
                    })

            result.output_files = new_files
            result.success = process.returncode == 0

        except Exception as error:
            self.logger.error(f"Error during code execution: {error}", exc_info=True)
            error_msg = str(error)
            result.error = ErrorResponse(
                type=type(error).__name__,
                message=error_msg
            )
            result.success = False

        result.std_out = self.out_string
        result.std_err = self.err_string
        result.code_runtime = int((time.time() - start_time) * 1000)
        self.logger.info(f"Code execution completed in {result.code_runtime}ms")
        return result

    async def terminate(self):
        """Terminate the running process if any"""
        if self.process and self.process.poll() is None:
            self.logger.info("Terminating running process")
            self.process.terminate()
            self.logger.debug("Process terminated")
        else:
            self.logger.debug("No process to terminate")

    async def cleanup(self):
        """Cleanup workspace and reload the environment"""
        self.logger.info("Starting workspace cleanup")
        # Remove all files in workspace except defaults
        files_removed = 0
        dirs_removed = 0
        
        for item in self.PYTHON_HOME.glob("*"):
            if item.name not in self.default_file_names:
                if item.is_file():
                    self.logger.debug(f"Removing file: {item}")
                    item.unlink()
                    files_removed += 1
                elif item.is_dir():
                    self.logger.debug(f"Processing directory: {item}")
                    for subitem in item.rglob("*"):
                        if subitem.is_file():
                            self.logger.debug(f"Removing file: {subitem}")
                            subitem.unlink()
                            files_removed += 1
                    item.rmdir()
                    dirs_removed += 1
        
        self.logger.info(f"Cleanup completed: removed {files_removed} files and {dirs_removed} directories")
        await self.load_environment()

    def base64_to_bytes(self, b64_data: str) -> bytes:
        """Convert base64 string to bytes."""
        try:
            return base64.b64decode(b64_data)
        except Exception as e:
            self.logger.error(f"Failed to decode base64 data: {e}")
            raise

    def read_file_as_base64(self, file_path: str) -> str:
        """Read file as base64 string."""
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            self.logger.error(f"Failed to read file as base64: {e}")
            raise
