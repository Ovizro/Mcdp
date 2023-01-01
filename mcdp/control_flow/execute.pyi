from typing import Any, Final, List, NoReturn, Optional, Tuple, Union, overload
from typing_extensions import Self

from ..objects import McdpObject
from ..variable import Selector, Position, NBTPath


class BaseInstruction(McdpObject):
    """
    Base class of all instructions of 'execute' command.
    """

    def __bool__(self) -> NoReturn: ...


class AlignInstruction(BaseInstruction):
    axes: Final[str]


class AnchoredInstruction(BaseInstruction):
    anchor: Final[str]


class AsInstruction(BaseInstruction):
    targets: Final[Selector]


class AtInstruction(BaseInstruction):
    targets: Final[Selector]


class FacingInstruction(BaseInstruction):
    entity: Final[bool]
    pos: Final[Position]
    targets: Final[Selector]
    anchor: str


class InInstruction(BaseInstruction):
    dimension: Final[str]


class PositionedInstruction(BaseInstruction):
    entity: Final[bool]
    targets: Final[Selector]
    pos: Final[Position]


class RotatedInstruction(BaseInstruction):
    entity: Final[bool]
    rot: Tuple[float, float]
    targets: Final[Selector]


class Case(McdpObject):
    """Base class for case instruction"""


class Blockcase(Case):
    pos: Final[Position]
    block: Final[str]


class DataCase(Case):
    type: Final[str]
    path: Final[NBTPath]
    pos: Final[Position]
    target: Final[Selector]
    source: Final[str]


class EntityCase(Case):
    targets: Final[Selector]


class PredicateCase(Case):
    predicate: Final[str]


class ScoreCase(Case):
    target: Final[Selector]
    target_obj: Final[str]
    ops: Final[str]
    source: Final[Selector]
    source_obj: Final[str]
    range: Final[str]


class ConditionInstruction(BaseInstruction):
    unless: Final[bool]
    case: Final[Case]


class StoreMode(McdpObject):
    """Base class for store instruction"""


class BlockStore(StoreMode):
    type: Final[str]
    target_pos: Final[Position]
    path: Final[NBTPath]
    scale: Final[float]


class BossbarStore(StoreMode):
    id: Final[str]
    value: Final[str]


class EntityStore(StoreMode):
    type: Final[str]
    target: Final[Selector]
    path: Final[NBTPath]
    scale: float


class ScoreStore(StoreMode):
    targets: Final[Selector]
    objective: Final[str]


class StorageStore(StoreMode):
    type: Final[str]
    target: Final[str]
    path: Final[NBTPath]


class StoreInstruction(BaseInstruction):
    store_success: Final[bool]
    mode: Final[StoreMode]


class Execute(McdpObject):
    def __new__(cls: type[Self], execobj: Union[Execute, BaseInstruction], *instructions: Union[Execute, BaseInstruction]) -> Self: ...
    def as_prefix(self, run_command: bool = False) -> str: ...
    def __call__(self, command: Any = False) -> None: ...
    @property
    def instructions(self) -> List[BaseInstruction]: ...