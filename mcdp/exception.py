class McdpError(Exception):
    __slots__ = []


class McdpValueError(McdpError):
    __slots__ = []


class McdpTypeError(McdpError):
    __slots__ = []


class McdpIndexError(McdpError):
    __slots__ = []


class McdpUnboundError(McdpError):
    __slots__ = []


class McdpRuntimeError(McdpError):
    __slots__ = []
    