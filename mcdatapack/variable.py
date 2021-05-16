import ujson
from typing import Any, Dict, Final, Optional, Union

from .counter import Counter
from .context import insert, comment
from .typings import Variable
class ScoreboardType(Variable):

    __slots__ = ["name", "criteria", "displayName", "counter", "linked"]

    def __init__(
        self,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[dict] = None,
    ):
        self.name = name
        self.criteria = criteria
        self.displayName = display

        super().__init__()

    def dumps(self) -> Optional[str]:
        if self.displayName:
            return "scoreboard objectives add {0} {1} {2}\n".format(
                self.name, self.criteria, ujson.dumps(self.displayName)
            )
        else:
            return "scoreboard objectives add {0} {1}\n".format(
                self.name, self.criteria
            )
    
    def remove(self) -> None:
        insert(f"scoreboard objectives remove {self.name}\n")

    def display(self, pos: str) -> None:
        insert(f"scoreboard objectives setdisplay {pos} {self.name}\n")

class ScoreType(ScoreboardType):

    __slots__ = ["name", "criteria", "displayName", "counter", "linked", "player"]

    def __init__(self, name: str, player: str = "#mcdp_main", *, criteria: str = "dummy", display: Optional[dict] = None):
        self.player = player
        super().__init__(name, criteria=criteria, display=display)

    def __add__(self, other: Union[int, "ScoreType"]) -> "ScoreType":
        +self.counter
        if isinstance(other, int):
            pass
        else:
            +other.counter