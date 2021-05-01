from typing import Dict

from .variable import Variable
from .aio_stream import Stream

class Environment:

    __slots__ = ["name", "var_list", "stream"]

    def __init__(self, name: str):
        self.name = name
        self.var_list: Dict[str, Variable] = {}

    def __getitem__(self, key: str) -> Variable:
        if not key in self.var_list:
            raise AttributeError(f"unfound var {key} in env {self.name}")
        return self.var_list[key]

    def __setitem__(self, name: str, instance: Variable) -> None:
        if name in self.var_list:
            if self.var_list[name] == instance:
                return
        self.var_list[name] = instance

    def activate(self) -> None:
        MCFunc.enter(self.name)

    def exit(self) -> None:
        MCFunc.exit(self.name)

    def __str__(self) -> str:
        return f"<env {self.name} in >"

class Context:

    __slots__ = ["stack"]
    
from io import StringIO
from .file_struct import BuildDirs

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