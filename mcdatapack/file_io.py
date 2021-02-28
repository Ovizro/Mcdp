from io import StringIO
from typing import Tuple

from .file_struct import BuildDirs
from .file_output import FileOutput, MCFunc, MCJson, MCTag

def insert(*content: Tuple[str]) -> None:
    if not MCFunc.writable():
        raise OSError("cannot insert command.")
    
    content: str = '\n'.join(content)
    if not content.endswith("\n"): 
        content += "\n"
    MCFunc.write(content)

_textCache = StringIO()
    
def comment(content: str) -> None:
    if not MCFunc.writable():
        raise OSError("cannot comment.")

    if '\n' in content:
        l = content.split("\n")
        MCFunc.write("#" + "\n#".join(l)+"\n")
    else:
        MCFunc.write('#'+content+"\n")