from typing import Any, Dict

from .stream import Stream
from .context import get_namespace

def get_predicate_stream(name: str) -> Stream:
    return Stream(name+".json", root=get_namespace()+"/predicates")