from typing import Dict, List, Literal, Union, Optional

from .typings import McdpBaseModel
from .config import check_mc_version

class MCStringObj(McdpBaseModel):
    
    def json(self, **kw) -> str:
        return super().json(exclude_none=True, **kw)

class Score(MCStringObj):
    name: str
    objective: str
    value: str
    
class ClickEvent(MCStringObj):
    action: Literal["open_url", "run_command", "suggest_command", "change_page", "copy_to_clipboard"]
    value: str

@check_mc_version('>=1.16')
def _hover_event_checker(
    action: Literal["show_text", "show_item", "show_entity"],
    value: Optional[str],
    contents: Optional[Union[str, list, dict]]
) -> None:
    if action == 'show_text':
        pass

class HoverEvent(MCStringObj):
    action: Literal["show_text", "show_item", "show_entity"]
    value: Optional[str] = None
    contents: Optional[Union[str, list, dict]] = None

    def __init__(
        self,
        *,
        action: str,
        value: Optional[str] = None,
        contents: Optional[Union[str, list, dict]] = None
    ) -> None:
        super().__init__(action=action, value=value,contents=contents)

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
    
    def __call__(self, text: Optional[str] = None, **kw):
        if text:
            kw["text"] = text
        return MCString(**self.dict(), **kw)

class MCString(MCSS):
    text: str = None
    translate: str = None
    with_: List[str] = None
    score: Score = None
    selector: str = None
    keybind: str = None
    nbt: str = None
    block: str = None
    entity: str = None
    storage: str = None
    extra: List["MCString"] = None
    