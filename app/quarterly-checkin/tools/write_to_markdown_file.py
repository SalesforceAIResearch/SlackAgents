def write_tool(content: str, document_name: str):
    """Write content as a markdown file to the employee's local directory
    
    :param content: The content to be written
    :type content: string
    :param document_name: The name of the document to be written to
    :type document_name: string 
    """
    with open(f"assets/{document_name}", "w") as f:
        f.write(content)
    return f"Successfully saved the report to {document_name}"