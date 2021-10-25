import ujson
from io import StringIO
from itertools import count
from functools import lru_cache
from itertools import count
from typing import Generator, Literal, Optional, Union, Dict

from .config import get_config
from .context import Context, insert, enter_stack_ops, leave_stack_ops
from .command import Position, Selector, Execute, ScoreCase, ConditionInstruction, AsInstruction
from .typings import Variable, McdpVar


@lru_cache(2)
def get_tag() -> str:
    return "Mcdp_" + get_config().namespace


_entity_counter = count(0)
_entity_factory = lambda: next(_entity_counter)
_stack_scb = None
_selector_self = Selector("@s")


def set_stack_scb(score) -> None:
    global _stack_scb
    _stack_scb = score


class Entity(Variable):

    __slots__ = ["id", "type", "tags"]

    def __init__(
            self,
            type: str,
            pos: Union[str, Position, "Entity"] = "~ ~ ~",
            nbt: Dict[str, Union[str, list, dict, bool, int, float]] = {},
            *,
            set_id: bool = True
    ) -> None:
        self.id = _entity_factory()
        self.type = type
        cmd = StringIO()

        if isinstance(pos, Entity) or issubclass(pos.__class__, Entity):
            cmd.write(f"execute at {Selector(pos)} run summon ")
        else:
            if isinstance(pos, str):
                pos = Position(pos)
            cmd.write("summon ")
        cmd.write(type)
        cmd.write(' ')
        cmd.write(str(pos))

        if not nbt.get("Tags", None):
            self.tags = [get_tag()]
        elif not get_tag() in nbt["Tags"]:
            nbt["Tags"].append(get_tag())
            self.tags = nbt["Tags"]
        nbt["Tags"] = self.tags

        nbt_string = ujson.dumps(nbt)
        cmd.write(' ')
        cmd.write(nbt_string)
        insert(cmd.getvalue())
        if set_id:
            insert(f"scoreboard players set {Selector(self)} entityID {self.id}")
        super().__init__()

    def __selector__(self) -> Selector:
        if self.is_stack_entity():
            return _selector_self
        return Selector("@e", "scores={entityID=%i}" % self.id, type=self.type, limit=1, tag=get_tag())

    def __str__(self) -> str:
        return str(self.__selector__())

    def is_stack_entity(self) -> bool:
        if not Context.stack:
            return False
        return Context.stack[-1] == self

    def remove(self) -> None:
        insert(f"kill {Selector(self)}")
    
    def add_tag(self, tag: str) -> None:
        insert(f"tag {Selector(self)} add {tag}")
    
    def remove_tag(self, tag: str) -> None:
        insert(f"tag {Selector(self)} remove {tag}")
    
    def apply(self) -> None: ...


class McdpStack(Entity):
    
    __slots__ = ["stack_id"]

    def __init__(self, stack_id: int) -> None:
        nbt = {
            "Invulnerable": True, "Invisible": True, "Marker": True,
            "NoGravity":    True, "Tags": ["Mcdp_stack", "stack_top"]
        }
        self.stack_id = stack_id
        if stack_id < 1:
            nbt["Tags"].append("Mcdp_home")
        else:
            Context.stack[-1].remove_tag("stack_top")
        super().__init__("armor_stand", nbt=nbt, set_id=False)
        insert("scoreboard players set @e[tag=stack_top,limit=1] mcdpStackID {0}".format(stack_id))

    def __selector__(self) -> Selector:
        if self.is_stack_entity():
            return _selector_self
        elif self.stack_id > 0:
            return Selector(
                "@e", "scores={mcdpStackID=%i}" % self.stack_id, 
                "tag=Mcdp_stack", limit=1, tag=get_tag())
        else:
            return Selector("@e", "tag=Mcdp_home", tag=get_tag())

    def remove(self) -> None:
        insert(f"scoreboard players remove {self} mcdpStackID 1")
        match_score = ScoreCase(_selector_self, "mcdpStackID", "=", Selector("@e", "tag=stack_top", tag=get_tag(), limit=1), "mcdpStackID")
        exc = Execute(
            AsInstruction(Selector("@e", "tag=Mcdp_stack", tag=get_tag())),
            ConditionInstruction(match_score)
        )
        exc("tag @s add stack_top")
        super().remove()


@enter_stack_ops
def _enter_stack(context: Context) -> None:
    stack = McdpStack(len(context.stack))
    context.stack.append(stack)

@leave_stack_ops
def _leave_stack(context: Context) -> None:
    stack: McdpStack = context.stack[-1]
    stack.remove()
    context.stack.pop()