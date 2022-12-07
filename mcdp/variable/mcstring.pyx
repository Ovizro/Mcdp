cimport cython
from libc.string cimport strrchr
from cpython cimport PyErr_Format, PyTuple_New, PyTuple_SET_ITEM, Py_INCREF

from enum import Enum
from typing import Union
from typing_extensions import Protocol

from .. import get_pack

try:
    import ujson as json
except ImportError:
    import json


class MCStringLike(Protocol):
    def __mcstr__(self) -> BaseString:
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


class RenderStyle(Enum):
    bold = BOLD
    italic = ITALIC
    underlined = UNDERLINED
    strikethrough = STRIKETHROUGH
    obfuscated = OBFUSCATED

    def __or__(self, other) -> int:
        cdef int val = self.value
        if isinstance(other, int):
            return val + <int>other
        elif isinstance(other, RenderStyle):
            return val + <int>other.value
        return NotImplemented
    

ColorName = str
T_MCStrColor = Union[ColorName, int, Color, str]
T_MCString = Union[MCStringLike, str, dict]


cdef str get_color_name(MCStr_Color color_id):
    return Color(color_id).name

cdef inline Version get_support_version():
    return get_pack().pack_info.support_version

def _model_encoder(obj):
    if isinstance(obj, StringModel):
        return (<StringModel>obj).to_dict()
    else:
        return str(obj)


cdef class StringModel(McdpObject):
    cpdef dict to_dict(self):
        return {}
    
    cpdef str to_json(self):
        return json.dumps(self.to_dict(), default=_model_encoder)
    
    def copy(self, **kwds):
        cdef dict attr = self.to_dict()
        attr.update(kwds)
        return type(self)(**attr)
    
    def __eq__(self, other):
        if not isinstance(other, StringModel):
            return NotImplemented
        if not type(self) is type(other):
            return False
        return self.to_dict() == other.to_dict()
    
    def __repr__(self):
        cdef const char* qualname = Py_TYPE_NAME(self)
        cdef const char* name = strrchr(qualname, ord('.'))
        if name == NULL:
            name = qualname
        else:
            name += 1
        return PyUnicode_FromFormat("%s(%S)", name, <void*>self)
    
    def __str__(self):
        return self.to_json()


cdef class Score(StringModel):
    def __cinit__(self, str name not None, str objective not None, *, str value = None):
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


cdef class ClickEvent(StringModel):
    def __cinit__(self, str action not None, *, str value not None):
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


cdef class HoverEvent(StringModel):
    def __cinit__(self, str action not None, *, str value = None, contents = None):
        if not action in ["show_text", "show_item", "show_entity"]:
            PyErr_Format(ValueError, "invalid click event action '%S'", <void*>action)
        if not contents is None:
            if not get_support_version()._ensure(None, None, None, "1.16"):
                raise McdpVersionError("'context' is not supported under Minecraft version 1.16")
            if action == 'show_text':
                if isinstance(contents, dict):
                    self.contents = DpStaticStr_FromDict(<dict>contents)
                else:
                    self.contents = <BaseString?>contents
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


cdef class HoverItem(StringModel):
    def __cinit__(self, str id not None, *, count = None, str tag = None):
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


cdef class HoverEntity(StringModel):
    def __cinit__(self, str type not None, *, name = None, str id = None):
        self.type = type
        if name is None or isinstance(name, BaseString):
            self.name = name
        else:
            self.name = DpStaticStr_FromObject(type)
        
    cpdef dict to_dict(self):
        cdef dict data = {"type": self.type}
        if not self.name is None:
            data["name"] = self.name
        if not self.id is None:
            data["id"] = self.id
        return data


cdef class MCSS(StringModel):
    def __cinit__(
            self,
            render = None,
            *,
            color = None,
            bint bold = False,
            bint italic = False,
            bint underlined = False,
            bint strikethrough = False,
            bint obfuscated = False,
            str font = None,
            **kwds
        ):
        self.render_flag = 0
        if bold:
            self.render_flag |= BOLD
        if italic:
            self.render_flag |= ITALIC
        if underlined:
            self.render_flag |= UNDERLINED
        if strikethrough:
            self.render_flag |= STRIKETHROUGH
        if obfuscated:
            self.render_flag |= OBFUSCATED

        if isinstance(render, RenderStyle):
            self.render_flag = render.value
        elif not render is None:
            self.render_flag = render

        if color is None:
            self.color = None
        elif isinstance(color, int):
            self.color = get_color_name(color)
        elif isinstance(color, Color):
            self.color = color.name
        else:
            if color.startswith('#') and not get_support_version()._ensure(None, None, None, "1.16"):
                raise McdpVersionError("hex color is not supported under Minecraft version 1.16")
            self.color = color

        self.font = font
    
    @property
    def bold(self):
        return bool(self.render_flag & BOLD)
    
    @bold.setter
    def bold(self, val):
        if val:
            self.render_flag |= BOLD
        else:
            self.render_flag &= ~BOLD
        
    @property
    def italic(self):
        return bool(self.render_flag & ITALIC)
    
    @italic.setter
    def italic(self, val):
        if val:
            self.render_flag |= ITALIC
        else:
            self.render_flag &= ~ITALIC

    @property
    def underlined(self):
        return bool(self.render_flag & UNDERLINED)
    
    @underlined.setter
    def underlined(self, val):
        if val:
            self.render_flag |= UNDERLINED
        else:
            self.render_flag &= ~UNDERLINED
    
    @property
    def strikethrough(self):
        return bool(self.render_flag & STRIKETHROUGH)
    
    @strikethrough.setter
    def strikethrough(self, val):
        if val:
            self.render_flag |= STRIKETHROUGH
        else:
            self.render_flag &= ~STRIKETHROUGH
    
    @property
    def obfuscated(self):
        return bool(self.render_flag & OBFUSCATED)
    
    @obfuscated.setter
    def obfuscated(self, val):
        if val:
            self.render_flag |= OBFUSCATED
        else:
            self.render_flag &= ~OBFUSCATED
    
    cpdef dict to_dict(self):
        cdef dict data = {}
        if not self.color is None:
            data["color"] = self.color
        if not self.font is None:
            data["font"] = self.font
        if self.render_flag & BOLD:
            data["bold"] = True
        if self.render_flag & ITALIC:
            data["italic"] = True
        if self.render_flag & UNDERLINED:
            data["underlined"] = True
        if self.render_flag & STRIKETHROUGH:
            data["strikethrough"] = True
        if self.render_flag & OBFUSCATED:
            data["obfuscated"] = True
        return data
    
    def __call__(self, str text not None, **kwds):
        return PlainString(text, style=self, **kwds)


cdef class BaseString(StringModel):
    def __cinit__(self, *args, MCSS style = None, list extra = None,
            str insertion = None, clickEvent = None, hoverEvent = None, **kwds):
        if type(self) is BaseString:
            raise NotImplementedError
        self.style = style or MCSS(**kwds)
        self._extra = extra or []
        self.insertion = insertion
        if not clickEvent is None and not isinstance(clickEvent, ClickEvent):
            self.clickEvent = ClickEvent(**clickEvent)
        else:
            self.clickEvent = clickEvent
        if not hoverEvent is None  and not isinstance(hoverEvent, HoverEvent):
            self.hoverEvent = HoverEvent(**hoverEvent)
    
    @property
    def extra(self):
        return list(self._extra)
    
    cpdef void extend(self, mcstr) except *:
        s = DpStaticStr_FromObject(mcstr)
        self._extra.append(s)
    
    cpdef UnionString join(self, strings):
        cdef UnionString newstr = UnionString()
        for i in strings:
            i = DpStaticStr_FromObject(i)
            newstr._extra.append(i)
            newstr._extra.append(self)
        newstr._extra.pop()
        return newstr
    
    cpdef void set_interactivity(self, str type, value) except *:
        if type == "insertion":
            self.insertion = value
        elif type == "click":
            if isinstance(value, dict):
                value = ClickEvent(**value)
            self.clickEvent = value
        elif type == "hover":
            if isinstance(value, dict):
                value = HoverEvent(**value)
            self.hoverEvent = value
        else:
            raise ValueError(
                "the interactivity type should be 'insertion', "
                "'click' or 'hover', not '%s'" % type
            )
    
    cpdef dict to_dict(self):
        cdef:
            dict data = MCSS.to_dict(self.style)
            list _extra
        if not self.insertion is None:
            data["insertion"] = self.insertion
        if not self.clickEvent is None:
            data["clickEvent"] = self.clickEvent
        if not self.hoverEvent is None:
            data["clickEvent"] = self.hoverEvent
        if self._extra:
            data["extra"] = self._extra
        return data
    
    def __add__(self, other):
        if not isinstance(other, BaseString):
            return NotImplemented
        return UnionString(self, other)
    
    def __mcstr__(self) -> BaseString:
        return self


@cython.final
cdef class UnionString(BaseString):
    def __cinit__(self, *args, **kwds):
        cdef BaseString i
        for i in args:
            if isinstance(i, UnionString):
                self._extra.extend(i._extra)
            else:
                self._extra.append(i)
    
    cpdef str to_json(self):
        return json.dumps(self.extra, default=_model_encoder)


@cython.final
cdef class PlainString(BaseString):
    def __cinit__(self, str text not None, **kwds):
        self.text = text
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["text"] = self.text
        return data
    
    def __mod__(self, with_):
        if isinstance(with_, tuple):
            with_ = list(with_)
            for i in range(len(with_)):
                with_[i] = DpStaticStr_FromObject(with_[i])
        else:
            with_ = (DpStaticStr_FromObject(with_),)

        cdef TranslatedString newstr = TranslatedString(self.text, *with_)
        return newstr


@cython.final
cdef class TranslatedString(BaseString):
    def __cinit__(self, str translate not None, *with_arg, list with_ = None, **kwds):
        self.translate = translate
        with_ = kwds.get("with", with_)
        if with_ is None:
            with_ = list(with_arg)

        cdef:
            Py_ssize_t size = len(with_)
            tuple w = PyTuple_New(size)
            
        for i in range(size):
            tmp = DpStaticStr_FromObject(with_[i])
            Py_INCREF(tmp)
            PyTuple_SET_ITEM(w, i, tmp)
        self.with_ = w
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["translate"] = self.translate
        if self.with_:
            data["with"] = list(self.with_)
        return data


@cython.final
cdef class ScoreString(BaseString):
    def __cinit__(self, score not None, **kwds):
        if isinstance(score, Score):
            self.score = <Score>score
        else:
            self.score = Score(**score)
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["score"] = self.score
        return data


@cython.final
cdef class EntityNameString(BaseString):
    def __cinit__(self, str selector not None, *, separator = None, **kwds):
        self.selector = selector
        if not separator is None:
            if not get_support_version()._ensure(None, None, None, "1.17"):
                raise McdpValueError("'separator' is not supported under Minecraft version 1.17")
            if isinstance(separator, BaseString):
                self.separator = <BaseString>separator
            else:
                self.separator = DpStaticStr_FromObject(separator)
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["selector"] = self.selector
        if not self.separator is None:
            data["separator"] = self.separator
        return data


@cython.final
cdef class KeybindString(BaseString):
    def __cinit__(self, str keybind not None, **kwds):
        self.keybind = keybind
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["keybind"] = self.keybind
        return data


@cython.final
cdef class NBTValueString(BaseString):
    def __cinit__(self, str nbt not None, *, bint interpret = False, separator = None,
            str block = None, str entity = None, str storage = None, **kwds):
        self.nbt = nbt
        self.interpret = interpret
        if not separator is None:
            if not get_support_version()._ensure(None, None, None, "1.17"):
                raise McdpValueError("'separator' is not supported under Minecraft version 1.17")
            if isinstance(separator, BaseString):
                self.separator = <BaseString>separator
            else:
                self.separator = DpStaticStr_FromObject(separator)
        if not block is None:
            self.block = block
        elif not entity is None:
            self.entity = entity
        elif not storage is None:
            self.storage = storage
        else:
            raise McdpValueError("no nbt source given")
    
    cpdef dict to_dict(self):
        cdef dict data = BaseString.to_dict(self)
        data["nbt"] = self.nbt
        if self.interpret:
            data["interpret"] = True
        if not self.separator is None:
            data["separator"] = self.separator
        if not self.block is None:
            data["block"] = self.block
        elif not self.entity is None:
            data["entity"] = self.entity
        elif not self.storage is None:
            data["storage"] = self.storage
        return data


def mcstring(text = None, **kwds) -> BaseString:
    if isinstance(text, str):
        return PlainString(text=text, **kwds)
    elif not text is None:
        return DpStaticStr_FromObject(text)
    return DpStaticStr_FromDict(kwds)


cdef object DpStrStyle_New(MCStr_Color color, int render, const char* font):
    if font == NULL:
        _font = None
    else:
        _font = font.decode()
    return MCSS(render, color=color, font=_font)

cdef object DpStaticStr_FromObject(object obj):
    cdef PyObject* fn_mcstr
    if isinstance(obj, BaseString):
        return obj
    elif isinstance(obj, str):
        return PlainString(<str>obj)
    elif isinstance(obj, dict):
        return DpStaticStr_FromDict(<dict>obj)
    elif obj is None:
        raise TypeError("expected 'T_String', but 'NoneType' found")
    else:
        fn_mcstr = _PyType_Lookup(type(obj), "__mcstr__")
        if fn_mcstr != NULL:
            return (<object>fn_mcstr)(obj)
        PyErr_Format(McdpTypeError, "unsupport type '%s'", Py_TYPE_NAME(obj))

cdef object DpStaticStr_FromDict(dict data):
    cdef type string_type
    if "text" in data:
        string_type = PlainString
    elif "translate" in data:
        string_type = TranslatedString
    elif "score" in data:
        string_type = ScoreString
    elif "selector" in data:
        string_type = EntityNameString
    elif "keybind" in data:
        string_type = KeybindString
    elif "nbt" in data:
        string_type = NBTValueString
    else:
        PyErr_Format(McdpValueError, "invalid mcstring dict %S", <void*>data)
    return string_type(**data)

cdef object DpStaticStr_FromString(const char* string):
    return PlainString(string.decode())

cdef object DpStaticStr_FromStyle(object style, object text):
    return PlainString(text, style=style)

cdef object DpStaticStr_FromStyleString(object style, const char* text):
    return PlainString(text.decode(), style=style)

cdef object DpStaticStr_Copy(object mcstr):
    cdef:
        BaseString s = mcstr
        type strcls = type(s)
    return strcls(**s.to_dict())

cdef dict DpStaticStr_ToDict(object mcstr):
    return (<BaseString?>mcstr).to_dict()