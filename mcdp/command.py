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
    targets: Union[Selector, str]

    def __init__(self, targets: Union[Selector, str]) -> None:
        McdpBaseModel.__init__(self, targets=targets)

    def __str__(self) -> str:
        return f"as {self.targets}"

class AtInstruction(Instruction):
    targets: Union[Selector, str]

    def __init__(self, targets: Union[Selector, str]) -> None:
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
        if entity:
            if not anchor:
                raise ValueError("Miss a argument 'anchor'.'")
            McdpBaseModel.__init__(
                self, targets=pos_or_targets, anchor=anchor, entity=True)
        else:
            if anchor:
                raise ValueError("Invalid argument 'anchor'.")
            if not isinstance(pos_or_targets, Position):
                pos = Position(pos_or_targets)
            else:
                pos = pos_or_targets
            McdpBaseModel.__init__(self, pos=pos, entity=entity)
        
    def __str__(self) -> str:
        if self.entity:
            return f"facing entity {self.targets} {self.anchor}"
        else:
            return f"facing {self.pos}"

class InInstruction(Instruction):
    dimension: str

    def __init__(self, dimension: str) -> None:
        McdpBaseModel.__init__(self, dimension=dimension)
    
    def __str__(self) -> str:
        return f"in {self.dimension}"

class PositionedInstruction(Instruction):
    entity: bool
    pos: Optional[Position] = None
    targets: Union[str, Selector, None] = None

    def __init__(self, pos_or_targets: Union[str, Position, Selector], *, entity: bool = False) -> None:
        if entity:
            McdpBaseModel.__init__(self, targets=pos_or_targets, entity=True)
        else:
            if not isinstance(pos_or_targets, Position):
                pos = Position(pos_or_targets)
            else:
                pos = pos_or_targets
            McdpBaseModel.__init__(self, pos=pos, entity=False)
    
    def __str__(self) -> str:
        if self.entity:
            return f"positioned as {self.targets}"
        else:
            return f"positioned {self.pos}"

class RotatedInstruction(Instruction):
    entity: bool
    rot: Optional[Tuple[Union[int, float], Union[int, float]]] = None
    targets: Union[str, Selector, None] = None

    def __init__(self, rot_or_targets: Union[Tuple, str, Selector], *, entity: bool = False) -> None:
        if entity:
            McdpBaseModel.__init__(self, targets=rot_or_targets, entity=True)
        else:
            McdpBaseModel.__init__(self, rot=rot_or_targets, entity=entity)

    def __str__(self) -> str:
        if self.entity:
            return f"rotated as {self.targets}"
        else:
            return f"rotated {self.rot[0]} {self.rot[1]}"


