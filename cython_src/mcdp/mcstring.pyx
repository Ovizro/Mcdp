import ujson
from enum import Enum

from .config import get_config


cdef inline Version get_support_version():
    return get_config().support_version


cdef class MCStringObject(_McdpBaseModel):
    pass


cdef class Score(MCStringObject):
    cdef readonly:
        str name
        str objective
        str value
    
    def __init__(self, str name not None, str objective not None, str value = None):
        self.name = name
        self.objective = objective
        self.value = value
    
    cpdef dict to_dict(self):
        cdef dict data = {
            "name": self.name,
            "objective": self.objective
        }
        if not self.value is None:
            data["value"] = self.value
        return data


cdef class ClickEvent(MCStringObject):
    cdef readonly:
        str action
        str value

    def __init__(self, str action not None, str value not None):
        if not action in ["open_url", "run_command", "suggest_command", 
                "change_page", "copy_to_clipboard"]:
            raise McdpValueError("Invalid click event action.")
        self.action = action
        self.value = value
    
    cpdef dict to_dict(self):
        cdef dict data = {
            "action": self.action,
            "value": self.value
        }
        return data


cdef class HoverEvent(MCStringObject):
    cdef readonly:
        str action
        str value
        contents
    
    def __init__(self, str action not None, str value = None, contents = None):
        if not action in ["show_text", "show_item", "show_entity"]:
            raise McdpValueError("Invalid click event action.")
        if get_support_version() >= "1.16":
            if contents is None:
                if value:
                    self.value = value
                    self.contents = None
                else:
                    raise ValueError("invalid string attrs 'hoverEvent'.")
            if action == 'show_text':
                if isinstance(contents, dict):
                    self.contents = MCString(**contents)
                else:
                    self.contents = <MCString?>contents
            elif action == 'show_item':
                if not isinstance(contents, dict):
                    raise ValueError("invalid string attrs 'hoverEvent'.")
                self.contents = HoverItem(**contents)
            elif action == 'show_entity':
                if not isinstance(_ontents, dict):
                    raise ValueError("invalid string attrs 'hoverEvent'.")
                self.contents = HoverEntity(**contents)
        else:
            if contents:
                raise VersionError(
                        "the attribute 'contents' only can be used in Minecraft 1.16+.")
            self.value = value
            self.contents = None
    
    cpdef dict to_dict(self):
        cdef dict data = {"action": self.action}
        if not self.value is None:
            data["value"] = self.value
        if not self.contents is None:
            data["contents"] = self.contents
        return data
    

cdef class HoverItem(MCStringObject):
    cdef readonly:
        str id
        uint8 count
        str tag
    
    def __init__(self, str id not None, count = None, str tag = None):
        self.id = id
        if count is None:
            self.count = 0
        else:
            self.count = count
        self.tag = tag
    
    cpdef dict to_dict(self):
        cdef dict data = {"id": self.id}
        if self.count > 0:
            data["count"] = self.count
        if not self.tag is None:
            data["tag"] = self.tag
        return data


cdef class HoverEntity(MCStringObject):
    cdef readonly:
        MCString name
        str type
        str id
    
    def __init__(self, str type not None, name = None, str id = None):
        self.type = type
        if name is None or isinstance(name, MCString):
            self.name = name
        else:
            self.name = MCString(type)
        
    
    cpdef dict to_dict(self):
        cdef dict data = {"id": self.id}
        if self.count > 0:
            data["count"] = self.count
        if not self.tag is None:
            data["tag"] = self.tag
        return data


class Color(Enum):
    black       = BLACK
    dark_blue   = DARK_BLUE
    dark_green  = DARK_GREEN
    dark_aqua   = DARK_AQUA
    dark_red    = DARK_RED
    dark_purple = DARK_PURPLE
    gold        = GOLD
    gray        = GRAY
    dark_gray   = DARK_GRAY
    blue        = BLUE
    green       = GREEN
    aqua        = AQUA
    red         = RED
    light_purple= LIGHT_PURPLE
    yellow      = YELLOW
    white       = WHITE


cdef class MCSS(MCStringObject):
    cdef readonly:
        str color
        bint bold
        bint italic
        bint underlined
        bint strikethrough
        bint obfuscated
        str font
        separator
        str insertion
        ClickEvent clickEvent
        HoverEvent hoverEvent
    
    def __init__(
        self,
        *,
        color = None,
        bint bold = False,
        bint italic = False,
        bint underlined = False,
        bint strikethrough = False,
        bint obfuscated = False,
        str font = None,
        separator = None,
        str insertion = None,
        ClickEvent clickEvent = None,
        HoverEvent hoverEvent = None
    ):
        if isinstance(color, Color):
            
