from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Type, Union
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
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, val: Union[str, "Position"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
        
    def __repr__(self) -> str:
        return f"Position{self._posXYZ}"
    
    def __str__(self) -> str:
        return " ".join([i.value for i in self._posXYZ])

class KeywordArg:

    __slots__ = ["name", "value"]

    def __init__(self, name: str, value: Union[str, Set["KeywordArg"]]) -> None:
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
    args: List[Union[KeywordArg, str]] = []

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

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, val: Union[str, "NBTPath"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
    
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
            McdpBaseModel.__init__(self, pos=pos_or_targets, entity=entity)
        
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
            McdpBaseModel.__init__(self, pos=pos_or_targets, entity=False)
    
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

_case_register: Dict[str, Type["Case"]] = {}

class Case(McdpBaseModel):

    def __init__(self, **data) -> None:
        super().__init__(**data)

    def __new__(cls, type: str, *args, **kwds) -> "Case":
        return _case_register[type](*args, **kwds)
    
    def __init_subclass__(cls, *, type: str) -> None:
        _case_register[type] = cls
        super().__init_subclass__()

class BlockCase(Case, type="block"):
    pos: Position
    block: str

    def __init__(self, pos: Union[str, Position], block: str) -> None:
        super().__init__(pos=pos, block=block)
    
    def __str__(self) -> str:
        return f"block {self.pos} {self.block}"

class BlocksCase(Case, type="blocks"):
    start: Position
    end: Position

    destination: Position

    scan_mode: Literal["all", "marked"]

    def __init__(
        self,
        start: Union[str, Position],
        end: Union[str, Position],
        destination: Union[str, Position],
        *,
        scan_mode: Literal["all", "marked"] = "all"
    ) -> None:
        super().__init__(start=start, end=end, destination=destination, scan_mode=scan_mode)

    def __str__(self) -> str:
        return f"blocks {self.start} {self.end} {self.destination} {self.scan_mode}"

class DataCase(Case, type="data"):
    type: Literal["block", "entity", "storage"]
    pos: Optional[Position] = None
    targets: Union[str, Selector, None] = None
    path: NBTPath

    def __init__(
        self,
        type: Literal["block", "entity", "storage"],
        pos_or_targets: Union[Position, str, Selector],
        path: Union[str, NBTPath]
    ) -> None:
        if type == "block":
            super().__init__(type=type, pos=pos_or_targets, path=path)
        else:
            super().__init__(type=type, targets=pos_or_targets, path=path)

    def __str__(self) -> str:
        if type == "block":
            return f"data block {self.pos} {self.path}"
        else:
            return f"data {self.type} {self.targets} {self.path}"

class EntityCase(Case, type="entity"):
    targets: Union[str, Selector]

    def __init__(self, targets: Union[str, Selector]) -> None:
        super().__init__(targets=targets)
    
    def __str__(self) -> str:
        return f"entity {self.targets}"

class PredicateCase(Case, type="predicate"):
    predicate: str

    def __init__(self, predicate: str) -> None:
        super().__init__(predicate=predicate)
    
    def __str__(self) -> str:
        return f"predicate {self.predicate}"

class ScoreCase(Case, type="score"):
    target: Union[str, Selector]
    target_obj: str
    ops: Literal["<", "<=", "=", ">=", ">", "matches"]
    source: Union[str, Selector, None] = None
    source_obj: Optional[str] = None
    range: Optional[str] = None

    def __init__(
        self,
        target: Union[str, Selector],
    ) -> None:
        super().__init__(target=target)
    
    def __str__(self) -> str:
        return f"score {self.target}"

class CaseInstruction(Instruction):
    unless: bool
    case: Case

    def __init__(self, case: Case, *, unless: bool = False) -> None:
        McdpBaseModel.__init__(self, case=case, unless=unless)

    def __str__(self) -> str:
        if self.unless:
            return "unless "
        else:
            return "if "

