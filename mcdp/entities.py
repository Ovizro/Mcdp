import ujson
from io import StringIO
from itertools import count
from functools import lru_cache
from itertools import count
from typing import Generator, Literal, Optional, Union, Dict

from .config import get_config
from .context import Context, insert, enter_stack_ops, leave_stack_ops
from .command import Position, Selector
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
            nbt: Dict[str, Union[str, list, dict, bool, int, float]] = {}
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

        if nbt.get("Tags", None):
            self.tags = [get_tag()]
        elif not get_tag() in nbt["Tags"]:
            self.tags = nbt["Tags"].append(get_tag())
        nbt["Tags"] = self.tags

        nbt_string = ujson.dumps(nbt)
        cmd.write(' ')
        cmd.write(nbt_string)
        insert(
                cmd.getvalue(),
                f"scoreboard players set {Selector(self)} entityID {self.id}"
        )
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

    def __init__(self, stack_id: int, *, home: bool = False) -> None:
        nbt = {
            "Invulnerable": True, "Invisible": True, "Marker": True,
            "NoGravity":    True, "Tags": ["Mcdp_stack", "stack_top"]
        }
        self.stack_id = stack_id
        if home:
            nbt["Tags"].append(get_tag() + "_home")
        else:
            insert("tag @s remove stack_top")
        super().__init__("armor_stand", nbt=nbt)
        insert("scoreboard players set @e[tag=stack_top,limit=1] mcdpStackID {0}".format(stack_id))

    def __selector__(self) -> Selector:
        if self.is_stack_entity():
            return _selector_self
        return Selector(
            "@e", "scores={mcdpStackID=%i}" % self.stack_id, 
            "tag=Mcdp_stack", type=self.type, limit=1, tag=get_tag())

    def remove(self) -> None:
        insert(
            "tag @e[tag=mcdp_stack_obj,scores={mcdpStackID=%i}] add stack_top" % (self.stack_id - 1)
        )
        super().remove()


@enter_stack_ops
def _enter_stack(context: Context, home: bool = False) -> None:
    stack = McdpStack(len(context.stack) - 1, home=home)
    context.stack.append(stack)

@leave_stack_ops
def _leave_stack(context: Context) -> None:
    stack: McdpStack = context.stack.pop()
    stack.remove()