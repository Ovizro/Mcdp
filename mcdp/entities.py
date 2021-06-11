from .context import insert
from .typings import Variable

class Entity(Variable):
    
    __slots__ = ["type", "tags"]