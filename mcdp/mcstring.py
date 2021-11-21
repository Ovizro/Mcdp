from enum import Enum, EnumMeta, unique
from pydantic import validator, Field
from typing import Dict, List, Any, Literal, Tuple, Union, Optional

from .typings import McdpBaseModel
from .config import check_mc_version, MinecraftVersionError


class MCStringObj(McdpBaseModel):

    def json(self, **kw) -> str:
        data = self.dict(**kw)
        return self.__config__.json_dumps(data)


class Score(MCStringObj):
    name: str
    objective: str
    value: Optional[str] = None


class ClickEvent(MCStringObj):
    action: Literal["open_url", "run_command", "suggest_command", "change_page", "copy_to_clipboard"]
    value: str


@check_mc_version('>=1.16')
def _hover_event_checker(
        action: Literal["show_text", "show_item", "show_entity"],
        value: Optional[str],
        _contents: Optional[Union[str, list, dict]]
) -> Tuple:
    if not _contents:
        if value:
            return value, _contents
        else:
            raise ValueError("invalid string attrs 'hoverEvent'.")

    if action == 'show_text':
        if isinstance(_contents, dict):
            contents = MCString(**_contents)
        else:
            contents = _contents
    elif action == 'show_item':
        if not isinstance(_contents, dict):
            raise ValueError("invalid string attrs 'hoverEvent'.")
        contents = HoverItem(**_contents)
    elif action == 'show_entity':
        if not isinstance(_contents, dict):
            raise ValueError("invalid string attrs 'hoverEvent'.")
        contents = HoverEntity(**_contents)

    return value, contents


@check_mc_version('<1.16')
def _hover_event_checker(
        action: Literal["show_text", "show_item", "show_entity"],
        value: Optional[str],
        _contents: Optional[Union[str, list, dict]]
) -> Tuple:
    if _contents:
        raise MinecraftVersionError(
                "the attribute 'contents' only can be used in Minecraft 1.16+.")
    return value, None


class HoverEvent(MCStringObj):
    action: Literal["show_text", "show_item", "show_entity"]
    value: Optional[str] = None
    contents: Optional[Union[str, list, "MCString", "HoverItem", "HoverEntity"]] = None

    def __init__(
            self,
            *,
            action: str,
            value: Optional[str] = None,
            contents: Optional[Union[str, list, dict]] = None
    ) -> None:
        value, contents = _hover_event_checker(action, value, contents)
        super().__init__(action=action, value=value, contents=contents)


class HoverItem(MCStringObj):
    id: str
    count: Optional[int] = None
    tag: Optional[str] = None


class HoverEntity(MCStringObj):
    name: Optional["MCString"] = None
    type: str
    id: Optional[str] = None


class EnumMetaclass(EnumMeta):

    __members__: Dict[str, Any]
    
    def __contains__(self, member: str) -> bool:
        return member in self.__members__.keys()

@unique
class Color(Enum, metaclass=EnumMetaclass):
    black       = 0
    dark_blue   = 1
    dark_green  = 2
    dark_aqua   = 3
    dark_red    = 4
    dark_purple = 5
    gold        = 6
    gray        = 7
    dark_gray   = 8
    blue        = 9
    green       = 10
    aqua        = 11
    red         = 12
    light_purple= 13
    yellow      = 14
    white       = 15


@check_mc_version('>=1.16')
def _check_color(color: str) -> None:
    if not color in Color and color.startswith('#'):
        try:
            int(color[1:])
        except (TypeError, ValueError):
            pass
        else:
            return
    elif color in Color:
        return

    raise ValueError("invalid string attrs 'color'.")


@check_mc_version('<1.16')
def _check_color(color: str) -> None:
    if not color in Color:
        raise ValueError("invalid string attrs 'color'.")


class MCSS(MCStringObj):
    color: str = None
    bold: bool = None
    italic: bool = None
    underlined: bool = None
    strikethrough: bool = None
    obfuscated: bool = None
    font: str = None
    separator: Union[str, dict] = None
    insertion: str = None
    clickEvent: ClickEvent = None
    hoverEvent: HoverEvent = None

    @validator('color')
    def colorValidator(cls, val: str) -> str:
        _check_color(val)
        return val

    def __call__(self, text: Optional[str] = None, **kw):
        if text:
            kw["text"] = text
        return MCString(**self.dict(), **kw)


class MCString(MCSS):
    text: str = None
    translate: str = None
    with_: list = Field(default=None, alias='with')
    score: Score = None
    selector: str = None
    keybind: str = None
    nbt: str = None
    block: str = None
    entity: str = None
    storage: str = None
    extra: list = None

    def __new__(cls, string: Any = None, **data) -> "MCString":
        if not string or isinstance(string, str):
            return MCSS.__new__(cls)
        elif hasattr(string, "__mcstr__"):
            return string.__mcstr__()
        else:
            raise TypeError(f"Invalid string {string}.")

    def __init__(self, string: Optional[Union[str, "MCString"]] = None, **data: Any) -> None:
        if string:
            if not isinstance(string, str):
                return
            data["text"] = string
        super().__init__(**data)

    def __mod__(self, _with: Union[str, "MCString", Tuple[Any, ...]]) -> "MCString":
        self = self.copy()

        if not self.translate:
            self.translate = self.text
            del self.text

        if isinstance(_with, self.__class__):
            _with = (_with,)
        elif isinstance(_with, tuple):
            _with = tuple((self.__class__(x) for x in _with))
        else:
            _with = (self.__class__(_with),)
        if self.with_:
            self.with_.extend(_with)
        else:
            self.with_ = list(_with)

        return self

    @classmethod
    def validate(cls, val):
        if isinstance(val, str) or hasattr(val, "__mcstr__"):
            return cls(val)
        elif isinstance(val, cls):
            return val
        else:
            raise TypeError("Invalid mcstring.")

    def dict(
            self,
            *,
            exclude_none: bool = True,
            **kwds
    ) -> Dict[str, Any]:
        data = super().dict(exclude_none=exclude_none, **kwds)
        if 'with_' in data:
            data['with'] = data.pop('with_')
        return data

    def __str__(self) -> str:
        return self.json()
