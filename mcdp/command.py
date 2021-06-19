from typing import Literal, Optional, Set, Union
from pydantic import constr

from .typings import McdpBaseModel, McdpVar

T_Range = constr(regex=r"(^\d+(\.\.\d*)?$)|(^\d*(\.\.\d+)?$)")
TU_Range = constr(regex=r"(^(\d+(\.\d+)?)(\.\.(\d+(\.\d+)?)?)?$)|(^(\d+(\.\d+)?)?(\.\.(\d+(\.\d+)?))?$)")
TF_Range = constr(regex=r"(^((-?\d+)(\.\d+)?)(\.\.((-?\d+)(\.\d+)?)?)?$)|(^((-?\d+)(\.\d+)?)?(\.\.((-?\d+)(\.\d+)?))?$)")
T_GameMode = constr(regex=r"!?(survival|spectator|adventure|creative)")

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

class SelectorScore(McdpBaseModel):
    objective: str
    value: T_Range
    
    def __str__(self) -> str:
        return f"{self.objective}={self.value}"

class SelectorAdvance(McdpBaseModel):
    name: str
    achieved: bool

    def __str__(self) -> str:
        return f"{self.name}={str(self.achieved).lower()}"

class Selector(McdpBaseModel):
    sel: Literal["@p", "@a", "@r", "@e", "@s"]
    
    x: Optional[Union[int, float]] = None
    y: Optional[Union[int, float]] = None
    z: Optional[Union[int, float]] = None
    
    dx: Optional[Union[int, float]] = None
    dy: Optional[Union[int, float]] = None
    dz: Optional[Union[int, float]] = None
    distance: Optional[TU_Range] = None
    
    scores: Set[SelectorScore] = set()
    tag: Set[str] = set()
    team: Set[str] = set()
    
    limit: Optional[T_Range] = None
    sort: Optional[Literal["nearest","furthest","random","arbitrary"]] = None
    level: Optional[T_Range] = None
    
    gamemode: Set[T_GameMode] = set()
    name: Set[str] = set()
    
    x_rotation: Optional[TF_Range] = None
    y_rotation: Optional[TF_Range] = None
    
    type: Optional[str] = None
    nbt: Optional[dict] = None
    advancements: None

class NBTPath(McdpVar):
    
    __slots__ = ["path"]
    
    def __init__(self, *args) -> None:
        self.path = list(args)

class Instruction(McdpBaseModel):
    
    __slots__ = []
    
    def __init__(self) -> None:
        raise NotImplementedError
    
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

class AaInstruction(Instruction):
    targets: Selector