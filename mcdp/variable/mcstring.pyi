from enum import Enum
from typing import Any, Dict, Final, List, Literal, Optional, Protocol, Tuple, Type, Union, overload
from typing_extensions import Self

from ..objects import McdpObject


class MCStringLike(Protocol):
    def __mcstr__(self) -> BaseString: ...


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


class RenderStyle(Enum):
    bold            = ...
    italic          = ...
    underlined      = ...
    strikethrough   = ...
    obfuscated      = ...

    def __or__(self, other: Union[int, RenderStyle]) -> int: ...


ColorName = Literal["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold",
                    "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]
T_MCStrColor = Union[ColorName, int, Color, str]
T_MCString = Union[MCStringLike, str, Dict[str, Any]]


class StringModel(McdpObject):
    def to_dict(self) -> Dict[str, Any]: ...
    def copy(self, **kwds) -> StringModel: ...


class Score(StringModel):
    name: str
    objective: str
    value: Optional[str]

    def __init__(self, *, name: str, objective: str, value: Optional[str] = None) -> None: ...


class ClickEvent(StringModel):
    action: Literal["open_url", "run_command", "suggest_command", "change_page", "copy_to_clipboard"]
    value: str
    
    def __init__(self, *, action: str, value: str) -> None: ...


class HoverEvent(StringModel):
    action: Literal["show_text", "show_item", "show_entity"]
    value: Optional[str]
    contents: Union[str, list, "BaseString", "HoverItem", "HoverEntity", None]
    
    @overload
    def __init__(self, *, action: Literal["show_text"], value: Optional[str] = None, contents: Optional[T_MCString] = None) -> None: ...
    @overload
    def __init__(self, *, action: Literal["show_item"], value: Optional[str] = None, contents: Union[Dict[str, Any], HoverItem, None] = None) -> None: ...
    @overload
    def __init__(self, *, action: Literal["show_entity"], value: Optional[str] = None, contents: Union[Dict[str, Any], HoverEntity, None] = None) -> None: ...


class HoverItem(StringModel):
    id: str
    count: Optional[int]
    tag: Optional[str]

    def __init__(self, id: str, *, count: Optional[int] = None, tag: Optional[str] = None) -> None: ...


class HoverEntity(StringModel):
    name: Optional["BaseString"]
    type: str
    id: Optional[str]


class MCSS(StringModel):
    color: str
    bold: bool
    italic: bool
    underlined: bool
    strikethrough: bool
    obfuscated: bool
    font: str

    def __new__(
        cls: Type[Self],
        render: Union[RenderStyle, int, None] = None,
        *,
        color: Optional[T_MCStrColor] = None,
        bold: bool = False,
        italic: bool = False,
        underlined: bool = False,
        strikethrough: bool = False,
        obfuscated: bool = False,
        font: Optional[str] = None,
    ) -> Self: ...
    def __call__(self, text: str, **kw) -> PlainString: ...


class BaseString(StringModel):
    style: Final[MCSS]
    extra: Final[List[BaseString]]
    insertion: str
    clickEvent: ClickEvent
    hoverEvent: HoverEvent

    def __new__(
        cls: Type[Self], 
        *args, 
        style: Optional[MCSS] = None,
        extra: Optional[List[BaseString]] = None,
        insertion: Optional[str] = None,
        clickEvent: Optional[ClickEvent] = None,
        hoverEvent: Optional[HoverEvent] = None,
        **kwds
    ) -> Self: ...
    def append(self, mcstr: T_MCString) -> None: ...
    @overload
    def set_interactivity(self, type: Literal["insertion"], value: str) -> None: ...
    @overload
    def set_interactivity(self, type: Literal["click"], value: Union[dict, ClickEvent]) -> None: ...
    @overload
    def set_interactivity(self, type: Literal["hover"], value: Union[dict, HoverEvent]) -> None: ...
    def __add__(self, other: BaseString) -> Self: ...
    def __mcstr__(self) -> Self: ...


class PlainString(BaseString):
    text: str

    def __new__(
        cls: Type[Self], 
        text: str, 
        *,
        style: Optional[MCSS] = ..., 
        extra: Optional[List[BaseString]] = ..., 
        insertion: Optional[str] = ..., 
        clickEvent: Optional[ClickEvent] = ..., 
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...
    def __mod__(self, with_: Union[T_MCString, Tuple[T_MCString, ...]]) -> TranslatedString: ...


class TranslatedString(BaseString):
    translate: Final[str]
    with_: Tuple[BaseString, ...]

    def __new__(
        cls: Type[Self],
        translate: str, 
        *with_arg: T_MCString,
        style: Optional[MCSS] = ..., 
        extra: Optional[List[BaseString]] = ..., 
        insertion: Optional[str] = ..., 
        clickEvent: Optional[ClickEvent] = ..., 
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...


class ScoreString(BaseString):
    score: Final[Score]

    def __new__(
        cls: Type[Self],
        score: Union[Score, Dict[str, Any]],
        *,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Optional[ClickEvent] = ...,
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...


class EntityNameString(BaseString):
    selector: str
    separator: PlainString

    def __new__(
        cls: Type[Self],
        selector: str,
        *,
        separator: Union[PlainString, str, None] = ...,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Optional[ClickEvent] = ...,
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...


class KeybindString(BaseString):
    keybind: Final[str]

    def __new__(
        cls: Type[Self],
        keybind: str,
        *,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Optional[ClickEvent] = ...,
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...


class NBTValueString(BaseString):
    nbt: Final[str]
    interpret: Final[bool]
    separator: Final[PlainString]
    block: Final[str]
    entity: Final[str]
    storage: Final[str]

    def __new__(
        cls: Type[Self],
        nbt: str,
        *,
        interpret: bool = ...,
        separator: Union[PlainString, str, None] = ...,
        block: Optional[str] = ...,
        entity: Optional[str] = ...,
        storage: Optional[str] = ...,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Optional[ClickEvent] = ...,
        hoverEvent: Optional[HoverEvent] = ...,
        # from MCSS
        render: Union[RenderStyle, int, None] = ...,
        color: Optional[T_MCStrColor] = ...,
        bold: bool = ...,
        italic: bool = ...,
        underlined: bool = ...,
        strikethrough: bool = ...,
        obfuscated: bool = ...,
        font: Optional[str] = ...,
    ) -> Self: ...


@overload
def mcstring(_obj: Union[Dict[str, Any], MCStringLike]) -> BaseString: ...
@overload
def mcstring(
    _obj: str,
    *,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Optional[ClickEvent] = ...,
    hoverEvent: Optional[HoverEvent] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> PlainString: ...