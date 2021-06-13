import ujson
from io import StringIO
from typing import Literal, Optional, Union, Dict
from .context import insert
from .typings import Variable, McdpVar

class PosComponent(McdpVar):
    
    __slots__ = ["type", "value"]
    
    def __init__(
        self,
        value: str,
        type: Optional[Literal["absolute", "relative", "local"]] = None
    ) -> None:
        self.value = value
        if '^' in value:
            int(value[1:])
            self.type = "local"
        elif '~' in value:
            int(value[1:])
            self.type = "relative"
        else:
            int(value)
            self.type = "absolute"
        if type and (type != self.type):
            raise ValueError("unsuit position value.")
        
    def __str__(self) -> str:
        return self.value
    
    __repr__ = __str__

class Position(McdpVar):

    __slots__ = ["_posXYZ", "type"]

    def __init__(self, pos: str) -> None:
        l = [PosComponent(i) for i in pos.split()]
        if len(l) != 3:
            raise ValueError("incorrect position length.")
        
        tid = 0
        for i in l:
            if i.type == "absolute":
                if tid == 3:
                    raise TypeError
                tid = 1
            elif i.type == "relative":
                if tid == 3:
                    raise TypeError
                tid = 2
            else:
                if tid < 3 and tid != 0:
                    raise TypeError
                tid = 3
        
        self._posXYZ = tuple(l)
        
    def __repr__(self) -> str:
        return f"Position{self._posXYZ}"
    
    def __str__(self) -> str:
        return " ".join([i.value for i in self._posXYZ])
        
class Entity(Variable):
    
    __slots__ = ["type", "tags"]
    
    def __init__(
        self,
        type: str,
        pos: Union[str, Position, None] = None,
        nbt: Optional[Dict[str, Union[str, list, dict]]] = None
    ) -> None:
        cmd = StringIO("summon ")
        cmd.write(type)
        if pos:
            if isinstance(pos, str):
                pos = Position(pos)
            cmd.write(' ')
            cmd.write(str(pos))
        if nbt:
            nbt_string = ujson.dumps(nbt)
            cmd.write(' ')
            cmd.write(nbt_string)
        super().__init__()
        
    def remove(self, direction: Union[str, Position]) -> None:...