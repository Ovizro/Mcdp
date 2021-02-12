from typing import Union

class MCDatapackError(Exception):
    pass

class VersionError(MCDatapackError):

    def __init__(self, req: Union[int, str], rel: Union[int, str], type: str = "mcdp") -> None:
        inf = f"require {type} {req} but get {rel}"
        super().__init__(inf)