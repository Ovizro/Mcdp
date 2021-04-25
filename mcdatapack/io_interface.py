from io import StringIO
from .file_struct import BuildDirs
from .output_stream import FileOutput, MCFunc, MCJson, MCTag

def insert(*contents: str) -> None:
    """
    Insert commends into correct context.
    When context is not writeable, throw OSError.
    """
    if not MCFunc.writable():
        raise OSError("cannot insert command.")
    
    content: str = '\n'.join(contents)
    if not content.endswith("\n"): 
        content += "\n"
    MCFunc.write(content)

_textCache = StringIO()
    
def comment(content: str) -> None:
    """
    Make a comment in correct file.
    """
    if not MCFunc.writable():
        raise OSError("cannot comment.")

    if '\n' in content:
        l = content.split("\n")
        MCFunc.write("#" + "\n#".join(l)+"\n")
    else:
        MCFunc.write('#'+content+"\n")