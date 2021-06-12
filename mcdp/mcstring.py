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
        super().__init__(action=action, value=value,contents=contents)
        
class HoverItem(MCStringObj):
    id: str
    count: Optional[int] = None
    tag: Optional[str] = None

class HoverEntity(MCStringObj):
    name: Optional["MCString"] = None
    type: str
    id: Optional[str] = None

_stand_color = ("black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple",
            "gold", "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple",
            "yellow", "white", "reset")

@check_mc_version('>=1.16')
def _check_color(color: str) -> None:
    if not color in _stand_color and color.startswith('#'):
        try:
            int(color[1:])
        except (TypeError, ValueError):
            pass
        else:
            return
    elif color in _stand_color:
        return
    
    raise ValueError("invalid string attrs 'color'.")
    
@check_mc_version('<1.16')
def _check_color(color: str) -> None:
    if not color in _stand_color:
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
    def _color(cls, val: str) -> str:
        _check_color(val)
        return val
    
    def __call__(self, text: Optional[str] = None, **kw):
        if text:
            kw["text"] = text
        return MCString(**self.dict(), **kw)

class MCString(MCSS):
    text: str = None
    translate: str = None
    with_: List[str] = Field(default=None, alias='with')
    score: Score = None
    selector: str = None
    keybind: str = None
    nbt: str = None
    block: str = None
    entity: str = None
    storage: str = None
    extra: list = None
    
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