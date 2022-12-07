/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE_API__mcdp__variable__nbtpath
#define __PYX_HAVE_API__mcdp__variable__nbtpath
#ifdef __MINGW64__
#define MS_WIN64
#endif
#include "Python.h"
#include "nbtpath.h"

static PyTypeObject *__pyx_ptype_4mcdp_8variable_7nbtpath_NBTPath = 0;
#define DpNBTPath_Type (*__pyx_ptype_4mcdp_8variable_7nbtpath_NBTPath)

static PyObject *(*__pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromObject)(PyObject *) = 0;
#define DpNBTPath_FromObject __pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromObject
static PyObject *(*__pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromString)(char const *) = 0;
#define DpNBTPath_FromString __pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromString
#if !defined(__Pyx_PyIdentifier_FromString)
#if PY_MAJOR_VERSION < 3
  #define __Pyx_PyIdentifier_FromString(s) PyString_FromString(s)
#else
  #define __Pyx_PyIdentifier_FromString(s) PyUnicode_FromString(s)
#endif
#endif

#ifndef __PYX_HAVE_RT_ImportFunction
#define __PYX_HAVE_RT_ImportFunction
static int __Pyx_ImportFunction(PyObject *module, const char *funcname, void (**f)(void), const char *sig) {
    PyObject *d = 0;
    PyObject *cobj = 0;
    union {
        void (*fp)(void);
        void *p;
    } tmp;
    d = PyObject_GetAttrString(module, (char *)"__pyx_capi__");
    if (!d)
        goto bad;
    cobj = PyDict_GetItemString(d, funcname);
    if (!cobj) {
        PyErr_Format(PyExc_ImportError,
            "%.200s does not export expected C function %.200s",
                PyModule_GetName(module), funcname);
        goto bad;
    }
    if (!PyCapsule_IsValid(cobj, sig)) {
        PyErr_Format(PyExc_TypeError,
            "C function %.200s.%.200s has wrong signature (expected %.500s, got %.500s)",
             PyModule_GetName(module), funcname, sig, PyCapsule_GetName(cobj));
        goto bad;
    }
    tmp.p = PyCapsule_GetPointer(cobj, sig);
    *f = tmp.fp;
    if (!(*f))
        goto bad;
    Py_DECREF(d);
    return 0;
bad:
    Py_XDECREF(d);
    return -1;
}
#endif

#ifndef __PYX_HAVE_RT_ImportType_proto
#define __PYX_HAVE_RT_ImportType_proto
enum __Pyx_ImportType_CheckSize {
   __Pyx_ImportType_CheckSize_Error = 0,
   __Pyx_ImportType_CheckSize_Warn = 1,
   __Pyx_ImportType_CheckSize_Ignore = 2
};
static PyTypeObject *__Pyx_ImportType(PyObject* module, const char *module_name, const char *class_name, size_t size, enum __Pyx_ImportType_CheckSize check_size);
#endif

#ifndef __PYX_HAVE_RT_ImportType
#define __PYX_HAVE_RT_ImportType
static PyTypeObject *__Pyx_ImportType(PyObject *module, const char *module_name, const char *class_name,
    size_t size, enum __Pyx_ImportType_CheckSize check_size)
{
    PyObject *result = 0;
    char warning[200];
    Py_ssize_t basicsize;
#if CYTHON_COMPILING_IN_LIMITED_API
    PyObject *py_basicsize;
#endif
    result = PyObject_GetAttrString(module, class_name);
    if (!result)
        goto bad;
    if (!PyType_Check(result)) {
        PyErr_Format(PyExc_TypeError,
            "%.200s.%.200s is not a type object",
            module_name, class_name);
        goto bad;
    }
#if !CYTHON_COMPILING_IN_LIMITED_API
    basicsize = ((PyTypeObject *)result)->tp_basicsize;
#else
    py_basicsize = PyObject_GetAttrString(result, "__basicsize__");
    if (!py_basicsize)
        goto bad;
    basicsize = PyLong_AsSsize_t(py_basicsize);
    Py_DECREF(py_basicsize);
    py_basicsize = 0;
    if (basicsize == (Py_ssize_t)-1 && PyErr_Occurred())
        goto bad;
#endif
    if ((size_t)basicsize < size) {
        PyErr_Format(PyExc_ValueError,
            "%.200s.%.200s size changed, may indicate binary incompatibility. "
            "Expected %zd from C header, got %zd from PyObject",
            module_name, class_name, size, basicsize);
        goto bad;
    }
    if (check_size == __Pyx_ImportType_CheckSize_Error && (size_t)basicsize != size) {
        PyErr_Format(PyExc_ValueError,
            "%.200s.%.200s size changed, may indicate binary incompatibility. "
            "Expected %zd from C header, got %zd from PyObject",
            module_name, class_name, size, basicsize);
        goto bad;
    }
    else if (check_size == __Pyx_ImportType_CheckSize_Warn && (size_t)basicsize > size) {
        PyOS_snprintf(warning, sizeof(warning),
            "%s.%s size changed, may indicate binary incompatibility. "
            "Expected %zd from C header, got %zd from PyObject",
            module_name, class_name, size, basicsize);
        if (PyErr_WarnEx(NULL, warning, 0) < 0) goto bad;
    }
    return (PyTypeObject *)result;
bad:
    Py_XDECREF(result);
    return NULL;
}
#endif


static int import_mcdp__variable__nbtpath(void) {
  PyObject *module = 0;
  module = PyImport_ImportModule("mcdp.variable.nbtpath");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "DpNBTPath_FromObject", (void (**)(void))&__pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromObject, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpNBTPath_FromString", (void (**)(void))&__pyx_api_f_4mcdp_8variable_7nbtpath_DpNBTPath_FromString, "PyObject *(char const *)") < 0) goto bad;
  __pyx_ptype_4mcdp_8variable_7nbtpath_NBTPath = __Pyx_ImportType(module, "mcdp.variable.nbtpath", "NBTPath", sizeof(struct DpNBTPathObject), __Pyx_ImportType_CheckSize_Warn);
   if (!__pyx_ptype_4mcdp_8variable_7nbtpath_NBTPath) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__mcdp__variable__nbtpath */
