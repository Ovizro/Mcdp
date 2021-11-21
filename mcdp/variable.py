from abc import abstractmethod
from collections import defaultdict
from functools import partial
from os import name
from typing import Any, DefaultDict, Dict, List, Literal, Optional, Type, TypeVar, Union

from .counter import Counter
from .context import insert
from .typings import Variable, VariableMeta, McdpVar
from .mcstring import MCString, Color
from .entities import McdpStack, get_tag
from .command import ConditionInstruction, ScoreCase, Selector
from .exceptions import *


class Scoreboard(Variable):

    __slots__ = ["name", "criteria", "display_name"]
    __accessible__ = ["name", "criteria", "display_name"]

    applied: List[str] = []
    collection: Dict[str, "Scoreboard"] = {}

    def __new__(
            cls,
            name: str,
            *,
            criteria: str = "dummy",
            display: Optional[Union[dict, MCString]] = None
    ):
        if name in cls.collection:
            instance = cls.collection[name]
            if instance.criteria != criteria:
                raise McdpVarError("Unmatch scoreboard data.", var=instance)
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
        if not self.used:
            return
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
                if c in Color:
                    insert(f"scoreboard objectives setdisplay {pos} {self.name}")
                    return
        else:
            insert(f"scoreboard objectives setdisplay {pos} {self.name}")
            return
        raise McdpValueError("Invalid scoreboard display position.")

    def set_value(self, selector: Union[str, Selector], value: int = 0) -> None:
        insert(f"scoreboard players set {selector} {self.name} {value}")


CONST_CACHE_NAME: str = "dpc_const"


def _get_selector(score: Union[int, "Score"]) -> Selector:
    if isinstance(score, int):
        stack_id = score
    else:
        stack_id = score.stack_id
    if stack_id == 0:
        return Selector("@e", "tag=Mcdp_home", tag=get_tag(), limit=1)
    elif stack_id == -1:
        return Selector("@e", "tag=stack_top", tag=get_tag(), limit=1)
    elif stack_id == -2:
        return Selector("@e", "tag=lower_stack", tag=get_tag(), limit=1)
    else:
        return Selector("@e", "tag=Mcdp_stack", tag=get_tag(), limit=1, scores="{mcdpStackID=%d}" % stack_id)


class Score(Variable):

    __slots__ = ["name", "stack_id", "scoreboard", "init_func", "selector"]
    __accessible__ = ["scoreboard"]

    def __init__(
            self,
            name: str,
            default: Union[int, "Score"] = 0,
            *,
            init: bool = True,
            stack_id: int = -1,
            selector: Union[Selector, str, None] = None,
            criteria: str = "dummy",
            display: Optional[Union[dict, MCString]] = None
    ) -> None:
        self.name = name
        if selector:
            self.selector = selector
        else:
            self.stack_id = stack_id
            if init:
                self.selector = _get_selector(self)
        self.scoreboard = Scoreboard(name, criteria=criteria, display=display)

        self.init_func = partial(self.set_value, default)
        if init:
            self.init_func()
            del self.init_func
        super().__init__()
        self.scoreboard.link(self)
    
    def __getattr__(self, attr: str) -> Any:
        if attr == "selector":
            self.selector = _get_selector(self)
        return self.__getattribute__(attr)

    def __iadd__(self, other: Union[int, "Score"]):
        +self.counter
        if isinstance(other, int):
            insert(
                    "scoreboard players add {0} {1} {2}".format(
                            self.selector, self.name, other
                    ))
        else:
            +other.counter
            insert(
                    "scoreboard players operation {0} {1} += {2} {3}".format(
                            self.selector, self.name,
                            other.selector, other.name
                    ))
        return self

    def __isub__(self, other: Union[int, "Score"]):
        +self.counter
        if isinstance(other, int):
            insert(
                    "scoreboard players remove {0} {1} {2}".format(
                            self.selector, self.name, other
                    ))
        else:
            +other.counter
            insert(
                    "scoreboard players operation {0} {1} -= {2} {3}".format(
                            self.selector, self.name,
                            other.selector, other.name
                    ))
        return self

    def __imul__(self, other: Union[int, "Score"]):
        +self.counter
        if isinstance(other, int):
            dpc_const.set_value(other)
            other = dpc_const
        +other.counter
        insert(
                "scoreboard players operation {0} {1} *= {2} {3}".format(
                        self.selector, self.name, other.selector, other.name
                ))
        return self

    def __itruediv__(self, other: Union[int, "Score"]):
        +self.counter
        if isinstance(other, int):
            dpc_const.set_value(other)
            other = dpc_const
        +other.counter
        insert(
                "scoreboard players operation {0} {1} /= {2} {3}".format(
                        self.selector, self.name, other.selector, other.name
                ))
        return self

    def __imod__(self, other: Union[int, "Score"]):
        +self.counter
        if isinstance(other, int):
            dpc_const.set_value(other)
            other = dpc_const
        +other.counter
        insert(
                "scoreboard players operation {0} {1} %= {2} {3}".format(
                        self.selector, self.name, other.selector, other.name
                ))
        return self
    
    def __eq__(self, other: Union["Score", int]) -> ConditionInstruction:
        if isinstance(other, int):
            return self.match(other)
        instr = ConditionInstruction(
            ScoreCase(
                self.selector, self.name,
                '=',
                other.selector, other.name
            )
        )
        return instr
    
    def __ne__(self, other: Union["Score", int]) -> ConditionInstruction:
        if isinstance(other, int):
            return self.match(other)
        instr = ConditionInstruction(
            ScoreCase(
                self.selector, self.name,
                '=',
                other.selector, other.name
            )
            , unless=True
        )
        return instr

    def set_value(self, value: Union[int, "Score"] = 0) -> None:
        if isinstance(value, int):
            self.scoreboard.set_value(self.selector, value)
        else:
            insert(
                    "scoreboard players operation {0} {1} = {2} {3}".format(
                            self.selector, self.name, value.selector, value.name
                    ))
    
    def match(self, range: Union[str, int], *, inverse: bool = False) -> ConditionInstruction:
        instr = ConditionInstruction(
            ScoreCase(
                self.selector, self.name,
                "matches", str(range)
            )
            , unless=inverse
        )
        return instr

    def apply(self) -> None:
        if not self.name in Scoreboard.applied:
            self.scoreboard.apply()

    def __mcstr__(self) -> MCString:
        return MCString(score={"name": str(self.selector), "objective": self.name})

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} objection {self.name} in stack {self.stack_id}>"


class _Cache:

    __slots__ = ["counter", "cache"]

    def __init__(self) -> None:
        self.counter = Counter('dpc')
        self.cache: DefaultDict[int, List[str]] = defaultdict(self.new_stack)

    def get(self, stack_id: int) -> str:
        dpc = self.cache[stack_id]
        if not dpc:
            name = self.get_name(self.counter)
            for i in self.cache.values():
                i.append(name)
            +self.counter
        return dpc.pop()

    def __getitem__(self, key: int) -> List[str]:
        return self.cache[key]

    def __setitem__(self, key: int, value: List[str]) -> None:
        self.cache[key] = value

    def new_stack(self) -> List[str]:
        return [self.get_name(i) for i in reversed(range(self.counter))]

    @staticmethod
    def get_name(cache_id: Union[int, Counter]) -> str:
        return "dpc_" + hex(cache_id)


class ScoreMeta(VariableMeta):

    def __instancecheck__(self, instance: Any) -> bool:
        if isinstance(instance, dp_score) and instance.simulation is self:
            return True
        return super().__instancecheck__(instance)


class ScoreCache(Score, metaclass=ScoreMeta):

    __slots__ = ["freed"]
    __accessible__ = []

    cache = _Cache()

    def __init__(self, default: Union[int, Score] = 0, *, init: bool = True, stack_id: int = -1) -> None:
        self.freed = False
        if stack_id != 0 and stack_id != -1:
            raise McdpValueError(f"Cannot use dp cahce object in the stack ID {stack_id}.")
        name = self.cache.get(stack_id)
        super().__init__(name, default, display={"text": "Mcdp Cache", "color": "dark_blue"}, init=init, stack_id=stack_id)

    def __add__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(self)
        ans += other
        -ans.counter
        return ans

    __radd__ = __add__

    def __sub__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(self)
        ans -= other
        -ans.counter
        return ans

    def __rsub__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(other)
        ans -= self
        return ans

    def __mul__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(self)
        ans *= other
        -ans.counter
        return ans

    __rmul__ = __mul__

    def __truediv__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(self)
        ans /= other
        -ans.counter
        return ans

    def __rtruediv__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(other)
        ans /= self
        -ans.counter
        return ans

    def __mod__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(self)
        ans %= other
        -ans.counter
        return ans

    def __rmod__(self, other: Union[int, Score]):
        if self.freed:
            raise McdpVarError("operation on a freed variable.", var=self)
        ans = self.__class__(other)
        ans %= self
        -ans.counter
        return ans

    def free(self) -> None:
        if not self.freed:
            dpc = self.cache[self.stack_id]
            dpc.append(self.name)
            self.freed = True

    def __del__(self) -> None:
        self.free()

    def __str__(self) -> str:
        return f"<mcdp cache {self.name} in stack {self.stack_id}>"


class dp_score(Score):

    __slots__ = ["simulation"]

    def __init__(
            self,
            name: str,
            default: Union[int, "Score"] = 0,
            *,
            init: bool = True,
            stack_id: int = -1,
            selector: Union[Selector, str, None] = None,
            criteria: str = "dummy",
            display: Optional[dict] = None,
            simulation: Optional[Type[ScoreCache]] = None
    ) -> None:
        if name.startswith("dpc_") and name != 'dpc_return' and name != "dpc_const":
            raise McdpVarError("The name of dp_score cannot start with 'dpc_'.")
        if simulation is self.__class__:
            simulation = None
        self.simulation = simulation
        super().__init__(
                name, default,
                init=init, stack_id=stack_id, selector=selector,
                criteria=criteria, display=display
        )

    def simulate(self, t_score: Type[ScoreCache]) -> None:
        if issubclass(t_score, ScoreCache):
            self.simulation = t_score
        else:
            raise TypeError("Only support similating a subclass of Score.")

    def __add__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__iadd__(other)

    __radd__ = __add__

    def __sub__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__isub__(other)

    def __rsub__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__rsub__(other)

    def __mul__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__mul__(other)

    __rmul__ = __mul__

    def __truediv__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__truediv__(other)

    def __rtruediv__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__rtruediv__(other)

    def __mod__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__mod__(other)

    def __rmod__(self, other: Score):
        if not self.simulation:
            return NotImplemented
        ans = self.simulation(self)
        return ans.__rmod__(other)

    def __str__(self) -> str:
        if not self.simulation:
            return super().__str__()
        else:
            return f"<{self.simulation.__name__} objection {self.name} in stack {self.stack_id}>"


class dp_int(ScoreCache):

    __slots__ = []

    def __str__(self) -> str:
        return f"<dp_int objection in stack {self.stack_id}>"


class StorageType(Variable):

    __slots__ = ["name"]
    cache = _Cache()

    def __init__(self) -> None:
        #self.name = self.cache.get(get_stack_id())
        super().__init__()

    @abstractmethod
    def path(self, key: Union[int, str]) -> str:
        raise NotImplementedError


class dp_array(StorageType):
    __slots__ = ["type", ]


class McdpVarError(McdpValueError):

    __slots__ = ["var"]

    def __init__(self, *arg: str, var: Optional[McdpVar] = None, **kw) -> None:
        self.var = var
        super().__init__(*arg, **kw)


T_Global = TypeVar("T_Global", dp_int, dp_score)
_global_var: List[Score] = []


def global_var(t_var: Type[T_Global], *args, **kwds) -> T_Global:
    var = t_var(*args, init=False, stack_id=0, **kwds)
    _global_var.append(var)
    return var

def init_global() -> None:
    for v in _global_var:
        v.init_func()
        del v.init_func

dpc_const = global_var(dp_score, CONST_CACHE_NAME)
entity_id = global_var(dp_score, "entityID")