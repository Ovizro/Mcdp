from libc.stdint cimport int64_t
from cpython cimport PyErr_Format, PyTuple_New, PyTuple_SET_ITEM, Py_INCREF
from ..cpython_interface cimport *


cdef class PathNode:
    def __cinit__(self, str name not None, PathNode next = None):
        self.name = name
        self.next = next
    
    cpdef PathNode copy(self, Py_ssize_t depth = -1):
        next = self.next.copy(depth - 1) if not self.next is None and depth else None
        return type(self)(self.name, next)
    
    def __eq__(self, other):
        if not isinstance(other, PathNode):
            return NotImplemented
        if self.next != (<PathNode>other).next:
            return False
        return self.name == (<PathNode>other).name
    
    def __repr__(self):
        return PyUnicode_FromFormat("Path(%U)", <void*>self.name)


cdef class NBTPath(McdpObject):
    def __cinit__(self, path):
        cdef PathNode node
        if isinstance(path, str):
            node = _DpPathNode_Split(path)
        else:
            node = path
        self.node = node
        self.size = 0
        while not node is None:
            self.size += 1
            node = node.next
    
    @property
    def named_tags(self):
        cdef:
            Py_ssize_t i = 0
            PathNode n = self.node
            tuple tags = PyTuple_New(self.size)
        while not n is None:
            name = n.name
            Py_INCREF(name)
            PyTuple_SET_ITEM(tags, i, name)
            n = n.next
            i += 1
        assert i == self.size
        return tags
    
    def __getitem__(self, int64_t key):
        if key < 0:
            key += self.size
        if key < 0:
            raise McdpIndexError("nbt path index out of range")
        elif key == self.size - 1:
            return self
        return NBTPath(self.node.copy(key))
    
    def __eq__(self, other):
        if not isinstance(other, NBTPath):
            return NotImplemented
        if self.size != (<NBTPath>other).size:
            return False
        return self.node == (<NBTPath>other).node

    def __len__(self):
        return self.size
    
    def __repr__(self):
        return PyUnicode_FromFormat("NBTPath(%S)", <void*>self)
    
    def __str__(self):
        if self.node is None:
            return "{}"

        cdef:
            PathNode n = self.node
            _PyUnicodeWriter writer
        _PyUnicodeWriter_Init(&writer)
        try:
            _PyUnicodeWriter_WriteStr(&writer, n.name)
            while not n.next is None:
                n = n.next
                _PyUnicodeWriter_WriteChar(&writer, ord('.'))
                _PyUnicodeWriter_WriteStr(&writer, n.name)
            return _PyUnicodeWriter_Finish(&writer)
        except:
            _PyUnicodeWriter_Dealloc(&writer)
            raise


cdef NBTPath empty_nbtpath = NBTPath(None)


def nbtpath(path = None):
    if path is None:
        return empty_nbtpath
    return NBTPath(path)


cdef PathNode _DpPathNode_Split(str string):
    cdef:
        Py_UCS4 ch
        Py_ssize_t prev = 0
        bint in_string = False
        int level = 0
        PathNode head = None
        PathNode node = None
    for i in range(len(string)):
        ch = PyUnicode_ReadChar(string, i)
        if ch == ord('.') and not in_string and not level:
            if head is None:
                head = node = PathNode(string[prev:i])
            else:
                node.next = PathNode(string[prev:i])
                node = node.next
            prev = i + 1
        elif ch == ord('"'):
            if i == 0 or PyUnicode_ReadChar(string, i - 1) != ord('\\'):
                in_string = not in_string
        elif ch == ord('{') and not in_string:
            level += 1
        elif ch == ord('}') and not in_string:
            level -= 1
    if in_string or level:
        PyErr_Format(ValueError, "invalid NBT path %U", <void*>string)
    if head is None:
        head = node = PathNode(string[prev:i + 1])
    else:
        node.next = PathNode(string[prev: i + 1])
    return head

cdef object DpNBTPath_FromObject(object obj):
    if obj is None:
        return empty_nbtpath
    return NBTPath(obj)

