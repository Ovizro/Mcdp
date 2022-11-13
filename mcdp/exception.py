class McdpError(Exception):
    __slots__ = []


class McdpInitalizeError(McdpError):
    __slots__ = []


class McdpRuntimeError(McdpError):
    __slots__ = []
    

class McdpValueError(McdpRuntimeError):
    __slots__ = []


class McdpTypeError(McdpRuntimeError):
    __slots__ = []


class McdpIndexError(McdpValueError):
    __slots__ = []


class McdpUnboundError(McdpRuntimeError):
    __slots__ = []

