from typing import Dict, Literal, Union, Optional

from .typings import McdpBaseModel
from .config import check_mc_version

class MCStringObj(McdpBaseModel):
    
    def json(self, **kw) -> str:
        return super().json(exclude_none=True, **kw)

class Score(MCStringObj):
    name: str
    objective: str
    value: str
    
class clickEvent(MCStringObj):
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

class hoverEvent(MCStringObj):
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
        super().__init__(**data)