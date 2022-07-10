cdef extern from "Python.h":
    ctypedef class types.FunctionType [object PyFunctionObject, check_size ignore]:
        cdef:
            object  fc_code         "func_code"
            object  fc_globals      "func_globals"
            tuple   fc_defaults     "func_defaults"
            dict    fc_kwdefaults   "func_kwdefaults"
            object  fc_closure      "func_closure"
            object  __doc__         "func_code"
            str     __name__        "func_name"
            dict    __dict__        "func_dict"
            object  __weakref__     "func_weakreflist"
            object  __module__      "func_module"
            dict    __annotations__ "func_annotation"
            str     __qualname__    "func_qualname"