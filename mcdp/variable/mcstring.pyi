from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Protocol, Union, overload

from ..objects import McdpObject


class MCStringLike(Protocol):
    def __mcstr__(self) -> MCString: ...


class Color(Enum):
    black       = ...
    dark_blue   = ...
    dark_green  = ...
    dark_aqua   = ...
    dark_red    = ...
    dark_purple = ...
    gold        = ...
    gray        = ...
    dark_gray   = ...
    blue        = ...
    green       = ...
    aqua        = ...
    red         = ...
    light_purple= ...
    yellow      = ...
    white       = ...


ColorName = Literal["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold",
                    "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]
T_MCStrColor = Union[ColorName, int, Color, str]
T_MCString = Union[MCStringLike, str, dict, Any]


class MCStringModel(McdpObject):
    def to_dict(self) -> dict: ...
    def copy(self, **kwds) -> MCStringModel: ...


class Score(MCStringModel):
    name: str
    objective: str
    value: Optional[str]

    def __init__(self, *, name: str, objective: str, value: Optional[str] = None) -> None: ...


class ClickEvent(MCStringModel):
    action: Literal["open_url", "run_command", "suggest_command", "change_page", "copy_to_clipboard"]
    value: str
    
    def __init__(self, *, action: str, value: str) -> None: ...


class HoverEvent(MCStringModel):
    action: Literal["show_text", "show_item", "show_entity"]
    value: Optional[str]
    contents: Union[str, list, "MCString", "HoverItem", "HoverEntity", None]
    
    @overload
    def __init__(self, *, action: Literal["show_text"], value: Optional[str] = None, contents: Optional[T_MCString] = None) -> None: ...
    @overload
    def __init__(self, *, action: Literal["show_item"], value: Optional[str] = None, contents: Union[Dict[str, Any], HoverItem, None] = None) -> None: ...
    @overload
    def __init__(self, *, action: Literal["show_entity"], value: Optional[str] = None, contents: Union[Dict[str, Any], HoverEntity, None] = None) -> None: ...


class HoverItem(MCStringModel):
    id: str
    count: Optional[int]
    tag: Optional[str]

    def __init__(self, id: str, *, count: Optional[int] = None, tag: Optional[str] = None) -> None: ...


class HoverEntity(MCStringModel):
    name: Optional["MCString"]
    type: str
    id: Optional[str]


class MCSS(MCStringModel):
    color: str
    bold: bool
    italic: bool
    underlined: bool
    strikethrough: bool
    obfuscated: bool
    font: str
    separator: Union[str, dict]
    insertion: str
    clickEvent: ClickEvent
    hoverEvent: HoverEvent

    def __init__(
        self,
        *,
        color: Optional[T_MCStrColor] = None,
        bold: bool = False,
        italic: bool = False,
        underlined: bool = False,
        strikethrough: bool = False,
        obfuscated: bool = False,
        font: Optional[str] = None,
        separator: Union[str, dict, None] = None,
        insertion: Optional[str] = None,
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = None,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = None
    ) -> None: ...
    def __call__(self, text: Optional[str] = None, **kw) -> MCString: ...


class MCString(MCSS):
    text: str
    translate: str
    with_: list
    score: Score
    selector: str
    keybind: str
    nbt: str
    block: str
    entity: str
    storage: str
    extra: List[MCString]

    def __init__(
        self, 
        _text = None,
        *,
        text: Optional[str] = None,
        translate: Optional[str] = None,
        with_: Optional[List[str]] = None,
        score = None,
        selector: Optional[str] = None,
        keybind: Optional[str] = None,
        nbt: Optional[str] = None,
        block: Optional[str] = None,
        entity: Optional[str] = None,
        storage: Optional[str] = None,
        extra: Optional[List[T_MCString]] = None,

        # inhert from MCSS
        color: Optional[T_MCStrColor] = None,
        bold: bool = False,
        italic: bool = False,
        underlined: bool = False,
        strikethrough: bool = False,
        obfuscated: bool = False,
        font: Optional[str] = None,
        separator: Union[str, dict, None] = None,
        insertion: Optional[str] = None,
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = None,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = None
    ) -> None: ...
    def extend(self, other: MCString) -> None: ...
    def __add__(self, other: MCString) -> MCString: ...
    def __mod__(self, _with: Union[tuple, T_MCString]) -> MCString: ...


def mcstring(
    _text: Optional[T_MCString] = None, *,
    # from MCString
    text: Optional[str] = None,
    translate: Optional[str] = None,
    with_: Optional[List[str]] = None,
    score = None,
    selector: Optional[str] = None,
    keybind: Optional[str] = None,
    nbt: Optional[str] = None,
    block: Optional[str] = None,
    entity: Optional[str] = None,
    storage: Optional[str] = None,
    extra: Optional[List[T_MCString]] = None,

    # from MCSS
    color: Optional[T_MCStrColor] = None,
    bold: bool = False,
    italic: bool = False,
    underlined: bool = False,
    strikethrough: bool = False,
    obfuscated: bool = False,
    font: Optional[str] = None,
    separator: Union[str, dict, None] = None,
    insertion: Optional[str] = None,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = None,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = None
) -> MCString: ...