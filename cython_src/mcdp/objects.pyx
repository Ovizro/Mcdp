cdef class McdpObject(object):
    pass


cdef class BaseNamespace(McdpObject):
    def __init__(self, name not None, bytes path = None):
        self.n_name = name.encode()
        if not path is None:
            self.n_path = path + self.n_name
        else:
            self.n_path = self.n_name
        
        self.n_tag = "Mcdp_" + name
        self.n_selector = "@e[tag=McdpHome,tag=%s,limit=1]" % self.n_tag