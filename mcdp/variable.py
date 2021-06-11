import ujson
from typing import Any, Dict, List, Literal, Optional, Union

from .counter import Counter
from .context import insert, get_stack_id
from .typings import Variable, McdpVar, McdpError
from .mcstring import MCString, _stand_color

class Scoreboard(McdpVar):

    __slots__ = ["name", "criteria", "display_name", "applied"]
    __accessible__ = ["name", "criteria", "display_name"]
    
    applied: List[str] = []
    collection: Dict[str, "Scoreboard"] = {}
    
    def __new__(cls,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[dict] = None
    ):
        if name in cls.collection:
            instance = cls.collection[name]
            if instance.criteria != criteria or instance.display != display:
                raise McdpVarError()
        else:
            return McdpVar.__new__(cls)

    def __init__(
        self,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[dict] = None
    ):
        self.name = name
        self.__class__.collection[name] = self
        self.criteria = criteria
        if display:
            self.display_name = MCString(**display)
        else:
            self.display_name = None

        super().__init__()

    def apply(self) -> None:
        if self.name in self.__class__.applied:
            raise McdpVarError("set up a scoreboard twice.", var=self)
        self.__class__.applied.append(self.name)
        if self.display_name:
            insert("scoreboard objectives add {0} {1} {2}".format(
                self.name, self.criteria, self.display_name.json()
            ))
        else:
            insert("scoreboard objectives add {0} {1}".format(
                self.name, self.criteria
            ))
    
    @classmethod
    def apply_all(cls) -> None:
        for s in cls.collection.values():
            s.apply()
    
    def remove(self) -> None:
        if self.name in self.__class__.applied:
            insert(f"scoreboard objectives remove {self.name}")

    def display(self, pos: str) -> None:
        if not pos in ["list", "sidebar", "belowName"]:
            if pos.startswith("sidebar.team."):
                c = pos[13:]
                if c in _stand_color:
                    insert(f"scoreboard objectives setdisplay {pos} {self.name}")
        else:        
            insert(f"scoreboard objectives setdisplay {pos} {self.name}")
        raise ValueError("invalid scoreboard display position.")

_score_cache: List["ScoreType"] = []
_score_cache_num: int = 0

def get_cache() -> Scoreboard:
    global _score_cache, _score_cache_num
    if _score_cache:
        return _score_cache.pop()
    else:
        name = "dpc_" + hex(_score_cache_num)
        scoreboard = ScoreType(name)
        _score_cache_num += 1
        return scoreboard

def free_cache(score: "ScoreType") -> None:
    _score_cache.append(score) 
    
def apply_cache() -> None:
    for s in range(_score_cache_num):
        s.apply()
        
def _get_selector(stack_id: int) -> str:
    if stack_id == get_stack_id():
        return "@s"
    else:
        return "@e[type=armor_stand,tag=mcdp_stack,scores={mcdpStackID=%i}]" % stack_id
    
class ScoreType(Variable):

    __slots__ = ["name", "stack_id", "scoreboard", "counter", "linked"]

    def __init__(self, name: str, *, criteria: str = "dummy", display: Optional[dict] = None):
        self.stack_id = get_stack_id()
        self.scoreboard = Scoreboard(name, criteria=criteria, display=display)

    def __add__(self, other: Union[int, "ScoreType"]) -> "ScoreType":
        +self.counter
        ans = get_cache()
        if isinstance(other, int):
            pass
        else:
            +other.counter
        return ans
        
    def apply(self) -> None:
        if not self.scoreboard in Scoreboard.applied:
            self.scoreboard.apply()

class McdpVarError(McdpError):
    
    __slots__ = ["var"]
    
    def __init__(self, *arg: str, var: Optional[McdpVar] = None, **kw) -> None:
        self.var = var
        super().__init__(*arg, **kw)
