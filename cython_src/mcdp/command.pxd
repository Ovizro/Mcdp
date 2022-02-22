from ._typing cimport McdpVar, McdpError
from .context cimport Context, _envs, dp_insert, dp_comment, dp_newline, get_extra_path 
from .exception cimport McdpValueError, McdpTypeError, McdpIndexError