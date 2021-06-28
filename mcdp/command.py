from os import name
from typing import Any, List, Literal, Optional, Set, Tuple, Union
from pydantic import constr

from .typings import McdpBaseModel, McdpVar

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

class SelectArg:

    __slots__ = ["name", "value"]

    def __init__(self, name: str, value: Union[str, Set["SelectArg"]]) -> None:
        self.name = name
        self.value = value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.value})"

    def __str__(self) -> str:
        if isinstance(self.value, set):
            value = '{' + ','.join((str(i) for i in self.value)) + '}'
        else:
            value = self.value
        return "{0}={1}".format(self.name, value)

class Selector(McdpBaseModel):
    name: Literal["@p", "@a", "@r", "@e", "@s"]
    args: List[Union[SelectArg, str]] = []

    def __init__(self, name: str, *args) -> None:
        if name in  ["@p", "@a", "@r", "@e", "@s"]:
            super().__init__(name=name, args = list(args))
        else:
            _name = name[:2]
            _args = name[2:-1].split(',')
            _args.extend(args)

            super().__init__(name=_name, args=_args)

    def __str__(self) -> str:
        if not self.args:
            return f"{self.name}"
        else:
            value = ','.join((str(i) for i in self.args))
            return f"{self.name}[{value}]"
    
    __repr__ = __str__

class NBTPath(McdpVar):
    
    __slots__ = ["path"]
    
    def __init__(self, *args: str) -> None:
        self.path = list(args)
    
    def __repr__(self) -> str:
        return f"NBTPath({self.__str__()})"

    def __str__(self) -> str:
        return '.'.join(self.path)

class Instruction(McdpBaseModel):
    
    __slots__ = []
    
    def __init__(self) -> None:
        raise NotImplementedError
    
    def __bool__(self) -> Any:
        return NotImplemented
    
    def __str__(self) -> str:
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f"Instruction({self})"
    
class AlignInstruction(Instruction):
    axes: str
    
    def __init__(self, axes: str) -> None:
        x = axes.count('x')
        y = axes.count('y')
        z = axes.count('z')
        if x>1 or y>1 or z>1 or x+y+z != len(axes):
            raise ValueError(
                "Axes should be any non-repeating combination of the characters 'x', 'y', and 'z'.")
        McdpBaseModel.__init__(self, axes=axes)
        
    def __str__(self) -> str:
        return f"align {self.axes}"

class AnchoredInstruction(Instruction):
    anchor: Literal["eyes", "feet"]
    
    def __init__(self, anchor: Literal["eyes", "feet"]) -> None:
        McdpBaseModel.__init__(self, anchor=anchor)
        
    def __str__(self) -> str:
        return f"anchored {self.anchor}"

class AsInstruction(Instruction):
    targets: Selector

    def __init__(self, targets: Union[Selector, str]) -> None:
        if isinstance(targets, str):
            targets = Selector(targets)
        McdpBaseModel.__init__(self, targets=targets)
    
    def __str__(self) -> str:
        return f"as {self.targets}"

class AtInstruction(Instruction):
    targets: Selector

    def __init__(self, targets: Union[Selector, str]) -> None:
        if isinstance(targets, str):
            targets = Selector(targets)
        McdpBaseModel.__init__(self, targets=targets)
    
    def __str__(self) -> str:
        return f"at {self.targets}"

class FacingInstruction(Instruction):
    entity: bool
    pos: Optional[Position] = None
    targets: Optional[Selector] = None
    anchor: Literal["eyes", "feet"]

    def __init__(
        self,
        pos_or_targets: Union[str, Position, Selector],
        anchor: Optional[Literal["eyes", "feet"]] = None,
        *,
        entity: bool = False
    ) -> None:
        ...
