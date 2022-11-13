cdef BaseString _default_sep = PlainString(" ")

cdef class _Console(McdpObject):
    @staticmethod
    def print(*texts, sep not None = _default_sep, target not None = SL_A):
        cdef BaseString s = DpStaticStr_FromObject(sep)
        cdef BaseString text = s.join(texts)
        DpConsole_Tell(target, text)
    
    @staticmethod
    cdef void _title(tuple texts, sep, MCTitle_Position pos, target) except *:
        cdef BaseString s = DpStaticStr_FromObject(sep)
        cdef BaseString text = s.join(texts)
        DpConsole_Title(target, pos, text)
    
    @staticmethod
    def title(*texts, sep not None = _default_sep, target not None = SL_A):
        _Console._title(texts, sep, TITLE, target)
        
    @staticmethod
    def subtitle(*texts, sep not None = _default_sep, target not None = SL_A):
        _Console._title(texts, sep, SUBTITLE, target)
        
    @staticmethod
    def actionbar(*texts, sep not None = _default_sep, target not None = SL_A):
        _Console._title(texts, sep, ACTIONBAR, target)
    
    @staticmethod
    def reset_title(target = SL_A):
        DpConsole_TitleReset(target)
    
    @staticmethod
    def set_time(int fadeIn, int stay, int fadeOut, target not None = SL_A):
        DpConsole_TitleSetTime(target, fadeIn, stay, fadeOut)


console = _Console()

cdef int DpConsole_Tell(object selector, object message) except -1:
    selector = DpSelector_FromObject(selector)
    message = DpStaticStr_FromObject(message)
    DpContext_Insert("tellraw %S %S", <void*>selector, <void*>message)
    return 0

cdef int DpConsole_TellString(object selector, const char* message) except -1:
    selector = DpSelector_FromObject(selector)
    DpContext_Insert("tell %S %s", <void*>selector, message)
    return 0

cdef int DpConsole_Print(object message) except -1:
    return DpConsole_Tell(SL_A, message)

cdef int DpConsole_PrintString(const char* message) except -1:
    return DpConsole_Print(DpStaticStr_FromString(message))

cdef int DpConsole_Title(object selector, MCTitle_Position pos, object message) except -1:
    cdef const char* pos_str
    if pos == ACTIONBAR:
        pos_str = "actionbar"
    elif pos == SUBTITLE:
        pos_str = "subtitle"
    else:
        pos_str = "title"
    selector = DpSelector_FromObject(selector)
    message = DpStaticStr_FromObject(message)
    DpContext_Insert("title %S %s %S", <void*>selector, pos_str, <void*>message)
    return 0

cdef int DpConsole_Show(MCTitle_Position pos, object message) except -1:
    return DpConsole_Title(SL_A, pos, message)

cdef int DpConsole_ShowString(MCTitle_Position pos, const char* message) except -1:
    return DpConsole_Show(pos, DpStaticStr_FromString(message))

cdef int DpConsole_TitleReset(object selector) except -1:
    selector = DpSelector_FromObject(selector)
    DpContext_Insert("title %S reset", <void*>selector)
    return 0

cdef int DpConsole_TitleClear(object selector) except -1:
    selector = DpSelector_FromObject(selector)
    DpContext_Insert("title %S clear", <void*>selector)
    return 0

cdef int DpConsole_TitleSetTime(object selector, int fadeIn, int stay, int fadeOut) except -1:
    selector = DpSelector_FromObject(selector)
    DpContext_Insert("title %S times %d %d %d", <void*>selector, fadeIn, stay, fadeOut)
    return 0
