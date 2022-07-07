class McdpObject(object):
    pass


class BaseNamespace(McdpObject):
    n_name: bytes
    n_path: bytes
    n_tag: str
    n_selector: str

    def __init__(self, name: str) -> None: ...