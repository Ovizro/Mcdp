from typing import Literal, Optional, Set, Union
from pydantic import constr

from .typings import McdpBaseModel, McdpVar

T_Range = constr(regex=r"(^\d+(\.\.\d*)?$)|(^\d*(\.\.\d+)?$)")
TU_Range = constr(regex=r"(^(\d+(\.\d+)?)(\.\.(\d+(\.\d+)?)?)?$)|(^(\d+(\.\d+)?)?(\.\.(\d+(\.\d+)?))?$)")
TF_Range = constr(regex=r"(^((-?\d+)(\.\d+)?)(\.\.((-?\d+)(\.\d+)?)?)?$)|(^((-?\d+)(\.\d+)?)?(\.\.((-?\d+)(\.\d+)?))?$)")
T_GameMode = constr(regex=r"!?(survival|spectator|adventure|creative)")

class SelectorScore(McdpBaseModel):
    objective: str
    value: T_Range
    
    def __str__(self) -> str:
        return f"{self.objective}={self.value}"

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