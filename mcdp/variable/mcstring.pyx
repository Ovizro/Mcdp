cimport cython
from libc.string cimport strrchr
from cpython cimport PyErr_Format, PyObject, PyList_New, PyList_SET_ITEM, Py_INCREF

from enum import Enum
from typing import Union, Any
from typing_extensions import Protocol

from .. import get_pack

try:
    import ujson as json
except ImportError:
    import json


class MCStringLike(Protocol):
    def __mcstr__(self) -> MCString:
        pass


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
    

ColorName = str
T_MCStrColor = Union[ColorName, int, Color, str]
T_MCString = Union[MCStringLike, str, dict, Any]


cdef str get_color_name(MCStr_Color color_id):
    return Color(color_id).name

cdef inline Version get_support_version():
    return get_pack().pack_info.support_version

def _model_encoder(obj):
    if isinstance(obj, MCStringModel):
        return (<MCStringModel>obj).to_dict()
    else:
        return str(obj)


cdef class MCStringModel(McdpObject):
    cpdef dict to_dict(self):
        return {}
    
    cpdef str to_json(self):
        return json.dumps(self.to_dict(), default=_model_encoder)
    
    def copy(self, **kwds):
        cdef dict attr = self.to_dict()
        attr.update(kwds)
        return type(self)(**attr)
    
    def __repr__(self):
        cdef const char* qualname = Py_TYPE_NAME(self)
        cdef const char* name = strrchr(qualname, ord('.'))
        if name == NULL:
            name = qualname
        else:
            name += 1
        return PyUnicode_FromFormat("%s(%S)", name, <PyObject*>self)
    
    def __str__(self):
        return self.to_json()


cdef class Score(MCStringModel):
    def __cinit__(self, *, str name not None, str objective not None, str value = None):
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


cdef class ClickEvent(MCStringModel):
    def __cinit__(self, *, str action not None, str value not None):
        if not action in ["open_url", "run_command", "suggest_command", 
                "change_page", "copy_to_clipboard"]:
            PyErr_Format(ValueError, "invalid click event action '%S'", <void*>action)
        self.action = action
        self.value = value
    
    cpdef dict to_dict(self):
        cdef dict data = {
            "action": self.action,
            "value": self.value
        }
        return data


cdef class HoverEvent(MCStringModel):
    def __cinit__(self, *, str action not None, str value = None, contents = None):
        if not action in ["show_text", "show_item", "show_entity"]:
            PyErr_Format(ValueError, "invalid click event action '%S'", <void*>action)
        if not contents is None:
            get_support_version()._ensure(None, None, None, "1.16")
            if action == 'show_text':
                if isinstance(contents, dict):
                    self.contents = MCString(**contents)
                else:
                    self.contents = <MCString?>contents
            elif action == 'show_item':
                if isinstance(contents, HoverItem):
                    self.contents = contents
                else:
                    self.contents = HoverItem(**contents)
            elif action == 'show_entity':
                if isinstance(contents, HoverEntity):
                    self.contents = contents
                else:
                    self.contents = HoverEntity(**contents)
        elif not value:
            raise ValueError("invalid string attrs 'hoverEvent'")
        else:
            self.value = value
            self.contents = None
    
    cpdef dict to_dict(self):
        cdef dict data = {"action": self.action}
        if not self.value is None:
            data["value"] = self.value
        if not self.contents is None:
            data["contents"] = self.contents
        return data


cdef class HoverItem(MCStringModel):
    def __cinit__(self, *, str id not None, count = None, str tag = None):
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


cdef class HoverEntity(MCStringModel):
    def __cinit__(self, *, str type not None, name = None, str id = None):
        self.type = type
        if name is None or isinstance(name, MCString):
            self.name = name
        else:
            self.name = MCString(type)
        
    cpdef dict to_dict(self):
        cdef dict data = {"type": self.type}
        if not self.name is None:
            data["name"] = self.name.to_dict()
        if not self.id is None:
            data["id"] = self.id
        return data


cdef class MCSS(MCStringModel):
    def __cinit__(
            self,
            *args,
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
            hoverEvent = None,
            **kwds
    ):
        if type(self) is MCSS:
            assert not args

        if color is None:
            self.color = None
        elif isinstance(color, int):
            self.color = get_color_name(color)
        elif isinstance(color, Color):
            self.color = color.name
        else:
            if color.startswith('#'):
                get_support_version()._ensure(None, None, None, "1.16")
            self.color = color
        self.bold = bold
        self.italic = italic
        self.underlined = underlined
        self.strikethrough = strikethrough
        self.obfuscated = obfuscated
        self.font = font
        if not separator is None and not isinstance(separator, (str, dict)):
            raise TypeError("'separator' must be a str or dict.")
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
            data["clickEvent"] = self.clickEvent.to_dict()
        if not self.hoverEvent is None:
            data["clickEvent"] = self.hoverEvent.to_dict()
        return data

    def __call__(self, text: Optional[str] = None, **kw):
        if text:
            kw["text"] = text
        return MCString(**self.to_dict(), **kw)

        
cdef class MCString(MCSS):
    def __cinit__(
        self,
        *,
        str text = None,
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
        self.text = text
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
        if not extra is None:
            self.extra = PyList_New(len(extra))
            for i in range(len(extra)):
                mcstr = DpStaticStr_FromObject(extra[i])
                Py_INCREF(mcstr)
                PyList_SET_ITEM(self.extra, i, mcstr)
        else:
            self.extra = []
    
    cpdef void extend(self, MCString other):
        self.extra.append(other)

    cpdef dict to_dict(self):
        cdef:
            dict data = MCSS.to_dict(self)
            list _extra
        if not self.text is None:
            data["text"] = self.text
        if not self.translate is None:
            data["translate"] = self.translate
        if not self.with_ is None:
            data["with"] = self.with_
        if not self.score is None:
            data["score"] = self.score.to_dict()
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
        if self.extra:
            _extra = PyList_New(len(self.extra))
            for i in range(len(self.extra)):
                dat = (<MCString?>(self.extra[i])).to_dict()
                Py_INCREF(dat)
                PyList_SET_ITEM(_extra, i, dat)
            data["extra"] = _extra
        return data
    
    def __iadd__(self, other):
        if isinstance(other, MCString):
            self.extend(other)
            return self
        else:
            return NotImplemented
    
    def __add__(self, other):
        cdef MCString newstr
        if isinstance(other, MCString):
            newstr = <MCString>DpStaticStr_Copy(self)
            newstr.extend(other)
            return newstr
        else:
            return NotImplemented
    
    def __mod__(self, _with):
        self = <MCString>DpStaticStr_Copy(self)

        if not self.translate:
            self.translate = self.text
            self.text = None
        
        if isinstance(_with, MCString):
            _with = (_with, )
        elif isinstance(_with, tuple):
            _with = list(_with)
            for i in range(len(_with)):
                _with[i] = DpStaticStr_FromObject(_with[i])
        else:
            _with = (DpStaticStr_FromObject(_with),)

        if self.with_:
            self.with_.extend(_with)
        else:
            self.with_ = list(_with)
        return self
    
    def __mcstr__(self) -> MCString:
        return self


def mcstring(text = None, **kwds) -> MCstring:
    if kwds:
        return MCString(text=text, **kwds)
    return DpStaticStr_FromObject(text)


cdef object DpStaticStr_FromObject(object obj):
    if isinstance(obj, MCString):
        return <MCString>obj
    elif isinstance(obj, dict):
        return MCString(**obj)
    elif hasattr(obj, "__mcstr__"):
        return obj.__mcstr__()
    elif obj is None:
        raise TypeError("expected 'T_MCString', but 'NoneType' found")
    else:
        return MCString(text=str(obj))


cdef object DpStaticStr_FromString(const char* string):
    return MCString(string.decode())


cdef object DpStaticStr_Copy(object mcstr):
    cdef MCString s = mcstr
    return MCString(**s.to_dict())