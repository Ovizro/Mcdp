from enum import Enum
from typing import Any, Dict, Final, Generic, Iterable, List, Literal, NoReturn, Optional, Protocol, Tuple, Type, TypeVar, Union, overload
from typing_extensions import Self, final

from ..objects import McdpObject


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


_T_StringObj = TypeVar("_T_StringObj",
    UnionString, PlainString, TranslatedString, ScoreString,
    EntityNameString, KeybindString, NBTValueString
)

class MCStringLike(Protocol, Generic[_T_StringObj]):
    def __mcstr__(self) -> _T_StringObj:
        pass


ColorName = Literal["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold",
                    "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]
T_MCStrColor = Union[ColorName, int, Color, str]
T_MCString = Union[MCStringLike, str, Dict[str, Any]]


class StringModel(McdpObject):
    def to_dict(self) -> Dict[str, Any]: ...
    def to_json(self) -> str: ...
    def copy(self, **kwds: Any) -> Self: ...


class Score(StringModel):
    name: str
    objective: str
    value: Optional[str]

    def __new__(cls: Type[Self], name: str, objective: str, *, value: Optional[str] = None) -> Self: ...


class ClickEvent(StringModel):
    action: Literal["open_url", "run_command", "suggest_command", "change_page", "copy_to_clipboard"]
    value: str
    
    def __new__(cls: Type[Self], action: str, *, value: str) -> Self: ...


class HoverEvent(StringModel):
    action: Literal["show_text", "show_item", "show_entity"]
    value: Optional[str]
    contents: Union[str, list, "BaseString", "HoverItem", "HoverEntity", None]
    
    @overload
    def __new__(
        cls: Type[Self],
        action: Literal["show_text"],
        *,
        value: Optional[str] = None,
        contents: Optional[T_MCString] = None
    ) -> Self: ...
    @overload
    def __new__(
        cls: Type[Self],
        action: Literal["show_item"],
        *,
        value: Optional[str] = None,
        contents: Union[Dict[str, Any], HoverItem, None] = None
    ) -> Self: ...
    @overload
    def __new__(
        cls: Type[Self],
        action: Literal["show_entity"],
        *,
        value: Optional[str] = None,
        contents: Union[Dict[str, Any], HoverEntity, None] = None
    ) -> Self: ...


class HoverItem(StringModel):
    id: str
    count: Optional[int]
    tag: Optional[str]

    def __new__(cls: Type[Self], id: str, *, count: Optional[int] = None, tag: Optional[str] = None) -> Self: ...


class HoverEntity(StringModel):
    name: Optional["BaseString"]
    type: str
    id: Optional[str]

    def __new__(cls: Type[Self], type: str, *, name: Optional[T_MCString] = ..., id: Optional[str] = ...) -> Self: ...

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
    def __call__(
        self,
        text: str, 
        extra: Optional[List[BaseString]] = ..., 
        insertion: Optional[str] = ..., 
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ..., 
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    ) -> PlainString: ...


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
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = None,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = None,
        **kwds
    ) -> NoReturn: ...
    def extend(self, mcstr: T_MCString) -> None: ...
    def join(self, strings: Iterable[T_MCString]) -> UnionString: ...
    @overload
    def set_interactivity(self, type: Literal["insertion"], value: str) -> None: ...
    @overload
    def set_interactivity(self, type: Literal["click"], value: Union[dict, ClickEvent]) -> None: ...
    @overload
    def set_interactivity(self, type: Literal["hover"], value: Union[dict, HoverEvent]) -> None: ...
    def __add__(self, other: BaseString) -> UnionString: ...
    def __mcstr__(self) -> Self: ...


@final
class UnionString(BaseString):
    def __new__(
        cls: Type[Self], 
        *args: BaseString,
        extra: Optional[List[BaseString]] = None
    ) -> Self: ...


@final
class PlainString(BaseString):
    text: str

    def __new__(
        cls: Type[Self], 
        text: str, 
        *,
        style: Optional[MCSS] = ..., 
        extra: Optional[List[BaseString]] = ..., 
        insertion: Optional[str] = ..., 
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ..., 
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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


@final
class TranslatedString(BaseString):
    translate: Final[str]
    with_: Final[Tuple[BaseString, ...]]

    def __new__(
        cls: Type[Self],
        translate: str, 
        *with_arg: T_MCString,
        with_: List[T_MCString] = ...,
        style: Optional[MCSS] = ..., 
        extra: Optional[List[BaseString]] = ..., 
        insertion: Optional[str] = ..., 
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ..., 
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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


@final
class ScoreString(BaseString):
    score: Final[Score]

    def __new__(
        cls: Type[Self],
        score: Union[Score, Dict[str, Any]],
        *,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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


@final
class EntityNameString(BaseString):
    selector: Final[str]
    separator: Final[Optional[BaseString]]

    def __new__(
        cls: Type[Self],
        selector: str,
        *,
        separator: Union[PlainString, str, None] = ...,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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


@final
class KeybindString(BaseString):
    keybind: Final[str]

    def __new__(
        cls: Type[Self],
        keybind: str,
        *,
        style: Optional[MCSS] = ...,
        extra: Optional[List[BaseString]] = ...,
        insertion: Optional[str] = ...,
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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


@final
class NBTValueString(BaseString):
    nbt: Final[str]
    interpret: Final[bool]
    separator: Final[Optional[BaseString]]
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
        clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
        hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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
def mcstring(text: Dict[str, Any]) -> BaseString: ...
@overload
def mcstring(text: MCStringLike[_T_StringObj]) -> _T_StringObj: ...
@overload
def mcstring(
    text: str,
    *,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
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
@overload
def mcstring(
    *,
    translate: str,
    with_: List[T_MCString] = ...,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> TranslatedString: ...
@overload
def mcstring(
    *,
    score: Union[Score, Dict[str, Any]],
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> ScoreString: ...
@overload
def mcstring(
    *,
    selector: str,
    separator: Union[PlainString, str, None] = ...,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> EntityNameString: ...
@overload
def mcstring(
    *,
    keybind: str,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> KeybindString: ...
@overload
def mcstring(
    *,
    nbt: str,
    block: str,
    interpret: bool = ...,
    separator: Union[PlainString, str, None] = ...,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> NBTValueString: ...
@overload
def mcstring(
    *,
    nbt: str,
    entity: str,
    interpret: bool = ...,
    separator: Union[PlainString, str, None] = ...,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> NBTValueString: ...
@overload
def mcstring(
    *,
    nbt: str,
    storage: str,
    interpret: bool = ...,
    separator: Union[PlainString, str, None] = ...,
    # from BaseString
    style: Optional[MCSS] = ...,
    extra: Optional[List[BaseString]] = ...,
    insertion: Optional[str] = ...,
    clickEvent: Union[ClickEvent, Dict[str, Any], None] = ...,
    hoverEvent: Union[HoverEvent, Dict[str, Any], None] = ...,
    # from MCSS
    render: Union[RenderStyle, int, None] = ...,
    color: Optional[T_MCStrColor] = ...,
    bold: bool = ...,
    italic: bool = ...,
    underlined: bool = ...,
    strikethrough: bool = ...,
    obfuscated: bool = ...,
    font: Optional[str] = ...,
) -> NBTValueString: ...
def mcstring(text: Optional[T_MCString] = ..., **kwds) -> BaseString: ...