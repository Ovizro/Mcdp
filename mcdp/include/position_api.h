/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE_API__mcdp__variable__position
#define __PYX_HAVE_API__mcdp__variable__position
#ifdef __MINGW64__
#define MS_WIN64
#endif
#include "Python.h"
#include "position.h"

static PyTypeObject *__pyx_ptype_4mcdp_8variable_8position_Component = 0;
#define DpComponent_Type (*__pyx_ptype_4mcdp_8variable_8position_Component)
static PyTypeObject *__pyx_ptype_4mcdp_8variable_8position_Position = 0;
#define DpPosition_Type (*__pyx_ptype_4mcdp_8variable_8position_Position)

static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_New)(float, float, float, enum MCPos_TypeFlag) = 0;
#define DpPosition_New __pyx_api_f_4mcdp_8variable_8position_DpPosition_New
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_FromObject)(PyObject *, enum MCPos_TypeFlag) = 0;
#define DpPosition_FromObject __pyx_api_f_4mcdp_8variable_8position_DpPosition_FromObject
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_FromString)(char const *) = 0;
#define DpPosition_FromString __pyx_api_f_4mcdp_8variable_8position_DpPosition_FromString
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetComponent)(PyObject *, Py_ssize_t) = 0;
#define DpPosition_GetComponent __pyx_api_f_4mcdp_8variable_8position_DpPosition_GetComponent
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetX)(PyObject *) = 0;
#define DpPosition_GetX __pyx_api_f_4mcdp_8variable_8position_DpPosition_GetX
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetY)(PyObject *) = 0;
#define DpPosition_GetY __pyx_api_f_4mcdp_8variable_8position_DpPosition_GetY
static PyObject *(*__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetZ)(PyObject *) = 0;
#define DpPosition_GetZ __pyx_api_f_4mcdp_8variable_8position_DpPosition_GetZ
static float (*__pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetOffset)(PyObject *) = 0;
#define DpPosComponent_GetOffset __pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetOffset
static enum MCPos_TypeFlag (*__pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetFlag)(PyObject *) = 0;
#define DpPosComponent_GetFlag __pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetFlag
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


static int import_mcdp__variable__position(void) {
  PyObject *module = 0;
  module = PyImport_ImportModule("mcdp.variable.position");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_New", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_New, "PyObject *(float, float, float, enum MCPos_TypeFlag)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_FromObject", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_FromObject, "PyObject *(PyObject *, enum MCPos_TypeFlag)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_FromString", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_FromString, "PyObject *(char const *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_GetComponent", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetComponent, "PyObject *(PyObject *, Py_ssize_t)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_GetX", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetX, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_GetY", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetY, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosition_GetZ", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosition_GetZ, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosComponent_GetOffset", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetOffset, "float (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpPosComponent_GetFlag", (void (**)(void))&__pyx_api_f_4mcdp_8variable_8position_DpPosComponent_GetFlag, "enum MCPos_TypeFlag (PyObject *)") < 0) goto bad;
  __pyx_ptype_4mcdp_8variable_8position_Component = __Pyx_ImportType(module, "mcdp.variable.position", "Component", sizeof(struct DpComponentObject), __Pyx_ImportType_CheckSize_Warn);
   if (!__pyx_ptype_4mcdp_8variable_8position_Component) goto bad;
  __pyx_ptype_4mcdp_8variable_8position_Position = __Pyx_ImportType(module, "mcdp.variable.position", "Position", sizeof(struct DpPositionObject), __Pyx_ImportType_CheckSize_Warn);
   if (!__pyx_ptype_4mcdp_8variable_8position_Position) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__mcdp__variable__position */