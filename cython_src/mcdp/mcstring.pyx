cimport cython
from cpython cimport PyObject, PyTuple_New, PyTuple_SET_ITEM, Py_INCREF

import ujson
from enum import Enum

from .config import get_config


cdef inline Version get_support_version():
    return get_config().support_version


cdef class MCStringObject(_McdpBaseModel):
    pass


cdef class Score(MCStringObject):
    def __init__(self, str name not None, str objective not None, str value = None):
        self.name = name
        self.objective = objective
        self.value = value
    
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {
            "name": self.name,
            "objective": self.objective
        }
        if not self.value is None:
            data["value"] = self.value
        return data


cdef class ClickEvent(MCStringObject):
    def __init__(self, str action not None, str value not None):
        if not action in ["open_url", "run_command", "suggest_command", 
                "change_page", "copy_to_clipboard"]:
            raise McdpValueError("Invalid click event action.")
        self.action = action
        self.value = value
    
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {
            "action": self.action,
            "value": self.value
        }
        return data


cdef class HoverEvent(MCStringObject):
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
                if not isinstance(contents, dict):
                    raise ValueError("invalid string attrs 'hoverEvent'.")
                self.contents = HoverEntity(**contents)
        else:
            if contents:
                raise VersionError(
                        "the attribute 'contents' only can be used in Minecraft 1.16+.")
            self.value = value
            self.contents = None
    
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {"action": self.action}
        if not self.value is None:
            data["value"] = self.value
        if not self.contents is None:
            data["contents"] = self.contents
        return data
    

cdef class HoverItem(MCStringObject):
    def __init__(self, str id not None, count = None, str tag = None):
        self.id = id
        if count is None:
            self.count = 0
        else:
            self.count = count
        self.tag = tag
    
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {"id": self.id}
        if self.count > 0:
            data["count"] = self.count
        if not self.tag is None:
            data["tag"] = self.tag
        return data


cdef class HoverEntity(MCStringObject):
    def __init__(self, str type not None, name = None, str id = None):
        self.type = type
        if name is None or isinstance(name, MCString):
            self.name = name
        else:
            self.name = MCString(type)
        
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {"type": self.type}
        if not self.name is None:
            data["name"] = self.name._json()
        if not self.id is None:
            data["id"] = self.id
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

    @classmethod
    def from_int(cls, MCStr_Color flag):
        cdef str nc = get_color_name(flag)
        return cls[nc]


cdef str get_color_name(MCStr_Color color_id):
    return Color(color_id).name


cdef class MCSS(MCStringObject):
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
            clickEvent = None,
            hoverEvent = None
    ):
        if color is None:
            self.color = None
        elif isinstance(color, int):
            self.color = get_color_name(color)
        elif isinstance(color, Color):
            self.color = color.name
        else:
            self.color = <str?>color
        self.bold = bold
        self.italic = italic
        self.underlined = underlined
        self.strikethrough = strikethrough
        self.obfuscated = obfuscated
        self.font = font
        if not separator is None and not isinstance(separator, (str, dict)):
            raise McdpTypeError("'separator' must be a str or dict.")
        self.separator = separator
        self.insertion = insertion
        if not clickEvent is None and not isinstance(clickEvent, ClickEvent):
            self.clickEvent = ClickEvent(**clickEvent)
        else:
            self.clickEvent = clickEvent
        if not hoverEvent is None  and not isinstance(hoverEvent, HoverEvent):
            self.hoverEvent = HoverEvent(**hoverEvent)
        else:
            self.hoverEvent = hoverEvent
    
    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = {}
        if not self.color is None:
            data["color"] = self.color
        if self.bold:
            data["bold"] = True
        if self.italic:
            data["italic"] = True
        if self.underlined:
            data["underlined"] = True
        if self.strikethrough:
            data["strikethrough"] = True
        if self.obfuscated:
            data["obfuscated"] = True
        if not self.font is None:
            data["font"] = self.font
        if not self.separator is None:
            data["separator"] = self.separator
        if not self.insertion is None:
            data["insertion"] = self.insertion
        if not self.clickEvent is None:
            data["clickEvent"] = self.clickEvent._json()
        if not self.hoverEvent is None:
            data["clickEvent"] = self.hoverEvent._json()
        return data

    def __call__(self, text: Optional[str] = None, **kw):
        if text:
            kw["text"] = text
        return MCString(**self.to_dict(), **kw)


cdef class MCString(MCSS):
    @cython.nonecheck(False)
    def __init__(
        self, 
        text = None,
        *,
        str translate = None,
        list with_ = None,
        score = None,
        str selector = None,
        str keybind = None,
        str nbt = None,
        str block = None,
        str entity = None,
        str storage = None,
        list extra = None,
        **kwds
    ):
        super().__init__(**kwds)
        if not text is None and not isinstance(text, str):
            self.text = str(text)
        else:
            self.text = <str>text
        self.translate = translate
        self.with_ = with_
        if not score is None and not isinstance(score, Score):
            self.score = Score(**score)
        else:
            self.score = <Score>score
        self.selector = selector
        self.keybind = keybind
        self.nbt = nbt
        self.block = block
        self.entity = entity
        self.storage = storage
        self.extra = extra

    @cython.nonecheck(False)
    cpdef dict to_dict(self):
        cdef dict data = MCSS.to_dict(self)
        if not self.text is None:
            data["text"] = self.text
        if not self.translate is None:
            data["translate"] = self.translate
        if not self.with_ is None:
            data["with"] = self._with
        if not self.score is None:
            data["score"] = self.score._json()
        if not self.selector is None:
            data["seletor"] = self.selector
        if not self.keybind is None:
            data["keybind"] = self.keybind
        if not self.nbt is None:
            data["nbt"] = self.nbt
        if not self.block is None:
            data["block"] = self.block
        if not self.entity is None:
            data["entity"] = self.entity
        if not self.storage is None:
            data["storage"] = self.storage
        if not self.extra is None:
            data["extra"] = self.extra
        return data
    
    def __mod__(self, _with):
        cdef:
            tuple tmp
            Py_ssize_t l_with
        self = self.copy()

        if not self.translate:
            self.translate = self.text
            self.text = None
        
        if isinstance(_with, MCString):
            _with = (_with, )
        elif isinstance(_with, tuple):
            l_with = len(_with)
            tmp = PyTuple_New(l_with)
            for i in range(l_with):
                val = (<tuple>_with)[i]
                val = fsmcstr(val)

                Py_INCREF(val)
                PyTuple_SET_ITEM(tmp, i, val)
            _with = tmp
        else:
            _with = (fsmcstr(_with),)
        if not self.with_ is None:
            self.with_.extend(_with)
        else:
            self.with_ = list(_with)

        return self
    
    @classmethod
    def validate(cls, val):
        return fsmcstr(val)


cpdef MCString fsmcstr(object t_mcstring):
    if isinstance(t_mcstring, str):
        return MCString(t_mcstring)
    elif isinstance(t_mcstring, MCString):
        return <MCString>t_mcstring
    elif hasattr(type(t_mcstring), "__mcstr__"):
        return t_mcstring.__mcstr__()
    else:
        raise McdpValueError("Invalid mcstring.")