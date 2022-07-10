from .objects cimport register_factory, BaseNamespace


ctypedef api object (*T_pFactory)(BaseNamespace nsp)

cdef api inline void DpNsp_property(const char* name, T_pFactory factory) except *:
    register_factory(name, factory)
