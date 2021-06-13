from pydantic import validate_arguments
from typing import Callable, List, Optional, Any

from .counter import Counter
from .typings import McdpVar, Variable
from .config import get_config
from .context import Context, insert

class MCFunction(McdpVar):
    
    __slots__ = ["overload", "path", "overload_counter"]
    
    def __init__(self, name: str, *, namespace: Optional[str] = None) -> None:
        namespace = namespace or get_config().namespace
        path = Context.get_relative_path() / name
        self.path = f"{namespace}:{path}"
        self.overload: List = []
        self.overload_counter: List[Counter] = []
    
    def register(self, func: Callable) -> None:
        func = validate_arguments(func)
        self.overload.append(func)
    
    def apply(self) -> None:
        ...
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        insert(f"function {self.path}")