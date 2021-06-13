from functools import partial
from typing import Any, Dict, List, Literal, Optional, Union

from .context import insert, get_stack_id
from .typings import Variable, McdpVar, McdpError
from .mcstring import MCString, _stand_color

class Scoreboard(McdpVar):

    __slots__ = ["name", "criteria", "display_name"]
    __accessible__ = ["name", "criteria", "display_name"]
    
    applied: List[str] = []
    collection: Dict[str, "Scoreboard"] = {}
    
    def __new__(cls,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[Union[dict, MCString]] = None
    ):
        if name in cls.collection:
            instance = cls.collection[name]
            if instance.criteria != criteria:
                raise McdpVarError()
            return instance
        else:
            return McdpVar.__new__(cls)

    def __init__(
        self,
        name: str,
        *,
        criteria: str = "dummy",
        display: Optional[Union[dict, MCString]] = None
    ):
        self.name = name
        self.__class__.collection[name] = self
        self.criteria = criteria
        if display:
            if isinstance(display, dict):
                self.display_name = MCString(**display)
            else:
                self.display_name = display
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
    
    def set_value(self, selector: str, value: int = 0) -> None:
        insert(f"scoreboard players set {selector} {self.name} {value}")
        
CONST_CACHE_NAME: str = "dpc_const"
        
def _get_selector(score: Union[int, "ScoreType"]) -> str:
    if isinstance(score, int):
        stack_id = score
    else:
        stack_id = score.stack_id
    if stack_id == get_stack_id():
        return "@s"
    else:
        return "@e[tag=mcdp_stack_obj,scores={mcdpStackID=%i}]" % stack_id
    
class ScoreType(Variable):

    __slots__ = ["name", "stack_id", "scoreboard", "counter", "linked"]
    __accessible__ = ["scoreboard"]

    def __init__(
        self,
        name: str,
        default: Union[int, "ScoreType"] = 0,
        *,
        criteria: str = "dummy",
        display: Optional[dict] = None
    ) -> None:
        
        self.name = name
        self.stack_id = get_stack_id()
        self.scoreboard = Scoreboard(name, criteria=criteria, display=display)
        self.set_value(default)
        super().__init__()

    def __iadd__(self, other: Union[int, "ScoreType"]):
        +self.counter
        if isinstance(other, int):
            insert(
                "scoreboard players add {0} {1} {2}".format(
                    _get_selector(self), self.name, other
                ))
        else:
            +other.counter
            insert(
                "scoreboard players operation {0} {1} += {2} {3}".format(
                    _get_selector(self), self.name,
                    _get_selector(other), other.name
                ))
        return self
    
    def __isub__(self, other: Union[int, "ScoreType"]):
        +self.counter
        if isinstance(other, int):
            insert(
                "scoreboard players remove {0} {1} {2}".format(
                    _get_selector(self), self.name, other
                ))
        else:
            +other.counter
            insert(
                "scoreboard players operation {0} {1} -= {2} {3}".format(
                    _get_selector(self), self.name,
                    _get_selector(other), other.name
                ))
        return self
    
    def __imul__(self, other: Union[int, "ScoreType"]):
        +self.counter
        if isinstance(other, int):
            name = CONST_CACHE_NAME
            self.scoreboard.set_value(name, other)
            scbd = self.name
        else:
            +other.counter
            name = _get_selector(other)
            scbd = other.name
        insert(
            "scoreboard players operation {0} {1} *= {2} {3}".format(
                _get_selector(self), self.name, name, scbd
            ))
        return self
    
    def __itruediv__(self, other: Union[int, "ScoreType"]):
        +self.counter
        if isinstance(other, int):
            name = CONST_CACHE_NAME
            self.scoreboard.set_value(name, other)
            scbd = self.name
        else:
            +other.counter
            name = _get_selector(other)
            scbd = other.name
        insert(
            "scoreboard players operation {0} {1} /= {2} {3}".format(
                _get_selector(self), self.name, name, scbd
            ))
        return self
    
    def __imod__(self, other: Union[int, "ScoreType"]):
        +self.counter
        if isinstance(other, int):
            name = CONST_CACHE_NAME
            self.scoreboard.set_value(name, other)
            scbd = self.name
        else:
            +other.counter
            name = _get_selector(other)
            scbd = other.name
        insert(
            "scoreboard players operation {0} {1} %= {2} {3}".format(
                _get_selector(self), self.name, name, scbd
            ))
        return self
    
    def set_value(self, value: Union[int, "ScoreType"] = 0) -> None:
        if isinstance(value, int):
            self.scoreboard.set_value(_get_selector(self), value)
        else:
            insert(
                "scoreboard players operation @s {0} = {1} {2}".format(
                    self.name, _get_selector(value), value.name
                ))
        
    def apply(self) -> None:
        if not self.name in Scoreboard.applied:
            self.scoreboard.apply()
    
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} objection {self.name} in stack {self.stack_id}>"
    
    __repr__ = __str__
    
_score_cache: List[List[str]] = []
_score_cache_num: int = 0
    
class ScoreCache(ScoreType):
    
    __slots__ = ["freed"]
    __accessible__ = []
    
    def __init__(self, default: Union[int, ScoreType] = 0) -> None:
        global _score_cache_num
        stack_id = get_stack_id()
        self.freed = False
        if stack_id+1 > len(_score_cache):
            l = [self.get_name(i) for i in reversed(range(_score_cache_num))]
            
            while stack_id+1 > len(_score_cache):
                _score_cache.append(l)
            
        dpc = _score_cache[stack_id]
        if not dpc:
            name = self.get_name(_score_cache_num)
            for i in _score_cache:
                i.append(name)
            _score_cache_num += 1
        name = dpc.pop()
        super().__init__(name, default, display={"text":"Mcdp Cache", "color":"dark_blue"})
    
    def __add__(self, other: Union[int, ScoreType]):
        ans = ScoreCache(self)
        ans += other
        -ans.counter
        return ans
    
    __radd__ = __add__
    
    def __sub__(self, other: Union[int, ScoreType]):
        ans = ScoreCache(self)
        ans -= other
        -ans.counter
        return ans
    
    def __rsub__(self, other: Union[int, ScoreType]):
        ans = ScoreCache(other)
        ans -= self
        return ans
    
    def __mul__(self, other: Union[int, ScoreType]):
        ans = ScoreCache(self)
        ans *= other
        -ans.counter
        return ans
    
    __rmul__ = __mul__
    
    def __truediv__(self, other: Union[int, ScoreType]) -> "ScoreCache":
        ans = ScoreCache(self)
        ans /= other
        -ans.counter
        return ans
    
    def __rtruediv__(self, other: Union[int, ScoreType]):
        ans = ScoreCache(other)
        ans /= self
        -ans.counter
        return ans
    
    def free(self) -> None:
        if not self.freed:
            dpc = _score_cache[self.stack_id]
            dpc.append(self.name)
            self.freed = True
        
    def __del__(self) -> None:
        self.free()

    @staticmethod
    def get_name(cache_id: int) -> str:
        return "dpc_" + hex(cache_id)
    
    @classmethod
    def apply_all(cls):
        for i in range(cls.score_cache_num):
            name = cls.get_name(i)
            if name in Scoreboard.applied:
                continue
            Scoreboard(name, display={"text":"Mcdp Cache", "color":"dark_blue"}).apply()
    
    def __str__(self) -> str:
        return f"<mcdp cache {self.name} in stack {self.stack_id}>"

class dp_score(ScoreType):
    pass

class dp_int(ScoreCache):
    
    def mcstr_ref(self) -> MCString:
        return MCString(score={"name":_get_selector(self), "objective":self.name})
    
    def __str__(self) -> str:
        return f"<mcdp int objection in the scoreboard {self.name}>"
    
    __repr__ = __str__

class McdpVarError(McdpError):
    
    __slots__ = ["var"]
    
    def __init__(self, *arg: str, var: Optional[McdpVar] = None, **kw) -> None:
        self.var = var
        super().__init__(*arg, **kw)
