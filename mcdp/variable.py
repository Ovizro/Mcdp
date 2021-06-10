import ujson
from typing import Any, Dict, List, Optional, Union

from .counter import Counter
from .context import insert
from .typings import Variable

class Scoreboard(Variable):

    __slots__ = ["name", "criteria", "display_name", "applied"]
    __accessible__ = ["name", "criteria", "display_name"]

    def __init__(
        self,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[dict] = None,
    ):
        self.name = name
        self.criteria = criteria
        self.display_name = display

        super().__init__()

    def apply(self) -> Optional[str]:
        if self.display_name:
            return "scoreboard objectives add {0} {1} {2}\n".format(
                self.name, self.criteria, ujson.dumps(self.display_name)
            )
        else:
            return "scoreboard objectives add {0} {1}\n".format(
                self.name, self.criteria
            )
    
    def remove(self) -> None:
        insert(f"scoreboard objectives remove {self.name}\n")

    def display(self, pos: str) -> None:
        insert(f"scoreboard objectives setdisplay {pos} {self.name}\n")

_current_owner: Optional[str] = None

_score_cache: List[str] = []
_score_cache_num: int = 0

def set_owner(name: str) -> None:
    global _current_owner
    _current_owner = name
    
def get_owner() -> str:
    if not _current_owner:
        raise RuntimeError("no owner defined.")
    return _current_owner

def get_cache() -> str:
    global _score_cache, _score_cache_num
    if _score_cache:
        return _score_cache.pop()
    else:
        name = "dpc_" + hex(_score_cache_num)
        _score_cache_num += 1
        return name

def free_cache(name: str) -> None:
    _score_cache.append(name) 
    
def apply_cache() -> None:
    for i in range(_score_cache_num):
        s = Scoreboard("dpc_"+hex(i))
    
class dp_score(Scoreboard):

    __slots__ = ["name", "criteria", "display_name", "counter", "linked", "player"]

    def __init__(self, name: str, player: str = "#mcdp_main", *, criteria: str = "dummy", display: Optional[dict] = None):
        self.player = player
        super().__init__(name, criteria=criteria, display=display)

    def __add__(self, other: Union[int, "dp_score"]) -> "dp_score":
        +self.counter
        if isinstance(other, int):
            pass
        else:
            +other.counter