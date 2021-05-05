from typing import Optional, Union

_current_counter: Optional["ContextCounter"] = None

class Counter:
    
    __slots__ = ["__count", "name"]
	
    def __init__(self, name: Optional[str] = None, init: int = 0):
        self.__count = init
        self.name = name
    
    @property
    def value(self) -> int:
        return self.__count
    
    def __pos__(self) -> None:
        self.__count += 1
    
    def __neg__(self) -> None:
        self.__count -= 1
    
    def __invert__(self) -> None:
        self.__count = 0
    
    def __add__(self, other: Union[int, "Counter"]) -> int:
        if isinstance(other, Counter):
            return self.__count + other.__count
        elif isinstance(other, int):
            return self.__count + other
        else:
            return NotImplemented
    
    __radd__ = __add__
    
    def __iadd__(self, other: Union[int, "Counter"]) -> "Counter":
        if isinstance(other, Counter):
            self.__count += other.__count
            return self
        elif isinstance(other, int):
            self.__count += other
            return self
        else:
            return NotImplemented
        
    def __sub__(self, other: Union[int, "Counter"]) -> int:
        if isinstance(other, Counter):
            return other.__count - self.__count
        elif isinstance(other, int):
            return other - self.__count
        else:
            return NotImplemented
    
    def __rsub__(self, other: int) -> int:
        if isinstance(other, int):
            return self.__count - other
        else:
            return NotImplemented
        
    def __isub__(self, other: Union[int, "Counter"]) -> "Counter":
        if isinstance(other, Counter):
            self.__count -= other.__count
            return self
        elif isinstance(other, int):
            self.__count -= other
            return self
        else:
            return NotImplemented
            
    def __int__(self) -> int:
        return self.__count
    
    def __bool__(self) -> bool:
        if self.__count > 0:
            return True
        else:
            return False
	
    def __repr__(self) -> str:
        if self.name:
            return f"<counter {self.name} with value {self.__count}>"
        else:
            return f"<counter {self.__count}>"
    
    def __str__(self) -> str:
        return str(self.__count)
    
class ContextCounter(object):
    
    __slots__ = ["dirs", "files", "commands", "chars"]
    
    def __init__(self):
        self.dirs = Counter("__dir__")
        self.files = Counter("__file__")
        self.commands = Counter("__command__")
        self.chars = Counter("__char__")
        
    def reset(self) -> None:
        ~self.dirs
        ~self.files
        ~self.commands
        ~self.chars
        
    def print_out(self) -> None:
        print(f"{self.dirs}+ dirs, {self.files} files,",
            f"{self.commands} commands, {self.chars} chars in total")
            
def get_counter():
    global _current_counter
    if not _current_counter:
        _current_counter = ContextCounter()
        
    return _current_counter
    
if __name__ == "__main__":
    c = get_counter()
    c0 = get_counter()
    assert c is c0
    
    +c.files
    +c.commands
    c.commands += 5
    c.print_out()
    print(int(c.commands) * 2)