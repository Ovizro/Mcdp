from .file_struct import BuildDirs
from .file_output import FileOutput, MCFunc, MCJson, MCTag

def insert(content: str) -> None:
    if not MCFunc.writable():
        raise OSError("cannot insert command.")
    if not content.endswith("\n"): 
        content += "\n"
    MCFunc.write(content)
    
def comment(content: str) -> None:
    
    insert("#")