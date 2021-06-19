import ujson
from io import StringIO
from typing import Literal, Optional, Union, Dict

from .context import insert
from .command import Position
from .typings import Variable, McdpVar
        
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