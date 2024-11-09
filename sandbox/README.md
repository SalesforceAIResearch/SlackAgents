# Python Code Execution Sandbox

A lightweight FastAPI service that provides a secure Python execution environment with support for data science packages and file handling. Perfect for building code interpreter tools that can run Python code snippets safely in isolated environments.

## Features

🛡️ **Secure Isolated Environment**: Runs code in a dedicated virtual environment.

🔬 **AI Ready**: NumPy: Numerical computing and arrays. Pandas: Data manipulation and analysis. Matplotlib: Data visualization. Scikit-learn: Machine learning tools.

📁 **File System Support**: Input file handling with base64 encoding. Output file generation and retrieval. Automatic workspace cleanup.

🌐 **Internet Access**: Secure HTTP requests. API integrations. Web scraping capabilities.

🔍 **Error Handling**: Detailed error messages. Stack trace reporting. Code context in errors. Standard output/error capture

⏱️ **Performance Monitoring**: Code execution timing. Execution status reporting

## Security Notes

- Code runs in an isolated virtual environment
- File system access is contained
- Resource monitoring recommended for production use

## Prerequisites

- Python 3.12+
- Docker (optional, for production)
- Conda (recommended for development)

## Quick Start

### Development Setup

1. Create and activate a conda environment:

```bash
conda create -n python-sandbox python=3.12 -y
conda activate python-sandbox
```

2. Clone the repository and install dependencies:

```bash
git clone https://github.com/airesearch-emu/SlackAgents
cd sandbox
pip install -r requirements.txt
```

3. Configure Authentication with API Key (Optional)

Users can set up authentication by setting `SANDBOX_API_KEY` in `.env` file. By default, this service does not require API key authentication.

```bash
cp .env.example .env
```
Then, users can input the key value in `SANDBOX_API_KEY` in `.env` file.

4. Run the development server:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```
The service will be available at `http://localhost:8080`

### Docker Setup (Production)

To run the service in a production environment, one can use Docker. The service uses `uvicorn` for relatively low latency, easy to use, and economical Python sandbox.

1. Configure Authentication with API Key (Optional). As above, users can set up authentication by setting `SANDBOX_API_KEY` in `.env` file. By default, this service does not require API key authentication.

2. Build and run the Docker container:

```bash
docker build -t python-sandbox .
docker run -p 8080:8080 python-sandbox
```

The service will be available at `http://localhost:8080`

## API Reference

After setting up the service, users can find the API documentation at: http://0.0.0.0:8080/docs . 

### POST `/submit`

Execute Python code in the sandbox environment.

#### Request Body

```json
{
    "code": "string",
    "files": [
        {
            "filename": "string",
            "b64_data": "string"
        }
    ]
}
```

- `code` (str): Python code to execute.
- `files` (List[FileInput]): List of input files to be used in the code execution.

#### Response

```json
{
    "success": "boolean",
    "final_expression": "any",
    "output_files": [
        {
            "filename": "string",
            "b64_data": "string"
}
    ],
    "error": {
        "type": "string",
        "message": "string"
    },
    "std_out": "string",
    "std_err": "string",
    "code_runtime": "integer"
}
```

## Example Usage

### HTTP Request

One can use any HTTP client to send the request. Here is an example using `curl`:

```bash
curl -X POST "http://localhost:8080/submit" -H "Content-Type: application/json" -d '{"code": "print(\"Hello, World!\")", "files": []}'
```

### Python Client

Here's a simple example using Python requests:

```python
import requests
import base64
# Prepare the code and files
code = """
import pandas as pd
import matplotlib.pyplot as plt
# Create a sample dataframe
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
# Plot the dataframe
plt.plot(df['x'], df['y'])
plt.savefig('plot.png')
"""
# Make API request
response = requests.post('http://localhost:8080/submit', 
    json={
        'code': code,
        'files': []
    }
)
# Process response
if response.json()['success']:
    # Handle output files
    for file in response.json()['output_files']:
        with open(file['filename'], 'wb') as f:
            f.write(base64.b64decode(file['b64_data']))
```

Note that besides `std_out` and `output_files`, the response also contains `final_expression` which is the value of the last expression in the code, and `std_err` which contains the error message if the code fails. These can be useful for building more complex agents with code interpreter tool.
