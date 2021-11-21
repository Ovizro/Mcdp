import ujson
from io import StringIO
from itertools import count
from functools import lru_cache
from itertools import count
from typing import Any, ClassVar, List, Union, Dict

from .config import get_config
from .context import Context, insert, enter_stack_ops, leave_stack_ops
from .command import Position, Selector, Execute, ScoreCase, ConditionInstruction, AsInstruction
from .typings import Variable, McdpVar


@lru_cache(2)
def get_tag() -> str:
    return "Mcdp_" + get_config().namespace


_entity_counter = count(0)
_entity_factory = lambda: next(_entity_counter)
_selector_self = Selector("@s")


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
            nbt["Tags"] = self.tags
        elif isinstance(nbt["Tags"], list) and not get_tag() in nbt["Tags"]:
            nbt["Tags"].append(get_tag())
            self.tags = nbt["Tags"]

        nbt_string = ujson.dumps(nbt)
        cmd.write(' ')
        cmd.write(nbt_string)
        insert(cmd.getvalue())
        if set_id:
            insert(f"scoreboard players set {Selector(self)} entityID {self.id}")
        super().__init__()

    def __selector__(self) -> Selector:
        return Selector("@e", "scores={entityID=%i}" % self.id, type=self.type, limit=1, tag=get_tag())

    def __str__(self) -> str:
        return str(self.__selector__())

    def remove(self) -> None:
        insert(f"kill {Selector(self)}")
    
    def add_tag(self, tag: str) -> None:
        insert(f"tag {Selector(self)} add {tag}")
    
    def remove_tag(self, tag: str) -> None:
        insert(f"tag {Selector(self)} remove {tag}")


class McdpStack(Entity):
    
    __slots__ = []

    stack_id: ClassVar[Any]

    def __init__(self) -> None:
        nbt = {
            "Invulnerable": True, "Invisible": True, "Marker": True,
            "NoGravity":    True, "Tags": ["Mcdp_stack", "stack_top"]
        }
        super().__init__("armor_stand", nbt=nbt, set_id=False)
    
    @staticmethod
    def __selector__() -> Selector:
        return Selector("@e", "tag=Mcdp_stack", tag=get_tag(), limit=1)

    def remove(self) -> None:
        insert(f"scoreboard players remove {self} mcdpStackID 1")
        match_score = ScoreCase(_selector_self, "mcdpStackID", "=", Selector("@e", "tag=stack_top", tag=get_tag(), limit=1), "mcdpStackID")
        exc = Execute(
            AsInstruction(Selector("@e", "tag=Mcdp_stack", tag=get_tag())),
            ConditionInstruction(match_score)
        )
        exc("tag @s add stack_top")
        super().remove()
    
    def __getitem__(self, key: str) -> Any:
        ...