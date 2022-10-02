/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE_API__mcdp__context
#define __PYX_HAVE_API__mcdp__context
#ifdef __MINGW64__
#define MS_WIN64
#endif
#include "Python.h"
#include "context.h"

static PyTypeObject *__pyx_ptype_4mcdp_7context__CHandlerMeta = 0;
#define DpHandlerMeta_Type (*__pyx_ptype_4mcdp_7context__CHandlerMeta)
static PyTypeObject *__pyx_ptype_4mcdp_7context_Context = 0;
#define DpContext_Type (*__pyx_ptype_4mcdp_7context_Context)

static struct DpHandlerMetaObject *(*__pyx_api_f_4mcdp_7context_DpHandlerMeta_New)(char const *, T_handler) = 0;
#define DpHandlerMeta_New __pyx_api_f_4mcdp_7context_DpHandlerMeta_New
static void (*__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetHandler)(struct DpHandlerMetaObject *, T_handler) = 0;
#define DpHandlerMeta_SetHandler __pyx_api_f_4mcdp_7context_DpHandlerMeta_SetHandler
static void (*__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetLinkHandler)(struct DpHandlerMetaObject *, T_connect) = 0;
#define DpHandlerMeta_SetLinkHandler __pyx_api_f_4mcdp_7context_DpHandlerMeta_SetLinkHandler
static void (*__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetPopHandler)(struct DpHandlerMetaObject *, T_connect) = 0;
#define DpHandlerMeta_SetPopHandler __pyx_api_f_4mcdp_7context_DpHandlerMeta_SetPopHandler
static PyObject *(*__pyx_api_f_4mcdp_7context_DpHandler_FromMeta)(struct DpHandlerMetaObject *, PyObject *) = 0;
#define DpHandler_FromMeta __pyx_api_f_4mcdp_7context_DpHandler_FromMeta
static PyObject *(*__pyx_api_f_4mcdp_7context_DpHandler_NewSimple)(char const *, T_handler) = 0;
#define DpHandler_NewSimple __pyx_api_f_4mcdp_7context_DpHandler_NewSimple
static PyObject *(*__pyx_api_f_4mcdp_7context_DpHandler_DoHandler)(PyObject *, PyObject *, PyObject *) = 0;
#define DpHandler_DoHandler __pyx_api_f_4mcdp_7context_DpHandler_DoHandler
static PyObject *(*__pyx_api_f_4mcdp_7context_DpContext_Get)(void) = 0;
#define DpContext_Get __pyx_api_f_4mcdp_7context_DpContext_Get
static PyObject *(*__pyx_api_f_4mcdp_7context_DpContext_Getback)(PyObject *) = 0;
#define DpContext_Getback __pyx_api_f_4mcdp_7context_DpContext_Getback
static PyObject *(*__pyx_api_f_4mcdp_7context_DpContext_New)(char const *) = 0;
#define DpContext_New __pyx_api_f_4mcdp_7context_DpContext_New
static int (*__pyx_api_f_4mcdp_7context_DpContext_Join)(PyObject *) = 0;
#define DpContext_Join __pyx_api_f_4mcdp_7context_DpContext_Join
static int (*__pyx_api_f_4mcdp_7context_DpContext_AddHnadler)(PyObject *, PyObject *) = 0;
#define DpContext_AddHnadler __pyx_api_f_4mcdp_7context_DpContext_AddHnadler
static int (*__pyx_api_f_4mcdp_7context_DpContext_AddHandlerSimple)(PyObject *, T_handler) = 0;
#define DpContext_AddHandlerSimple __pyx_api_f_4mcdp_7context_DpContext_AddHandlerSimple
static int (*__pyx_api_f_4mcdp_7context_DpContext_InsertV)(char const *, va_list) = 0;
#define DpContext_InsertV __pyx_api_f_4mcdp_7context_DpContext_InsertV
static int (*__pyx_api_f_4mcdp_7context_DpContext_Insert)(char const *, ...) = 0;
#define DpContext_Insert __pyx_api_f_4mcdp_7context_DpContext_Insert
static int (*__pyx_api_f_4mcdp_7context_DpContext_CommentV)(char const *, va_list) = 0;
#define DpContext_CommentV __pyx_api_f_4mcdp_7context_DpContext_CommentV
static int (*__pyx_api_f_4mcdp_7context_DpContext_Comment)(char const *, ...) = 0;
#define DpContext_Comment __pyx_api_f_4mcdp_7context_DpContext_Comment
static int (*__pyx_api_f_4mcdp_7context_DpContext_FastComment)(char const *) = 0;
#define DpContext_FastComment __pyx_api_f_4mcdp_7context_DpContext_FastComment
static int (*__pyx_api_f_4mcdp_7context_DpContext_Newline)(unsigned int) = 0;
#define DpContext_Newline __pyx_api_f_4mcdp_7context_DpContext_Newline
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


static int import_mcdp__context(void) {
  PyObject *module = 0;
  module = PyImport_ImportModule("mcdp.context");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandlerMeta_New", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandlerMeta_New, "struct DpHandlerMetaObject *(char const *, T_handler)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandlerMeta_SetHandler", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetHandler, "void (struct DpHandlerMetaObject *, T_handler)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandlerMeta_SetLinkHandler", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetLinkHandler, "void (struct DpHandlerMetaObject *, T_connect)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandlerMeta_SetPopHandler", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandlerMeta_SetPopHandler, "void (struct DpHandlerMetaObject *, T_connect)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandler_FromMeta", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandler_FromMeta, "PyObject *(struct DpHandlerMetaObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandler_NewSimple", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandler_NewSimple, "PyObject *(char const *, T_handler)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpHandler_DoHandler", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpHandler_DoHandler, "PyObject *(PyObject *, PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Get", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Get, "PyObject *(void)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Getback", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Getback, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_New", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_New, "PyObject *(char const *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Join", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Join, "int (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_AddHnadler", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_AddHnadler, "int (PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_AddHandlerSimple", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_AddHandlerSimple, "int (PyObject *, T_handler)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_InsertV", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_InsertV, "int (char const *, va_list)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Insert", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Insert, "int (char const *, ...)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_CommentV", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_CommentV, "int (char const *, va_list)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Comment", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Comment, "int (char const *, ...)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_FastComment", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_FastComment, "int (char const *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "DpContext_Newline", (void (**)(void))&__pyx_api_f_4mcdp_7context_DpContext_Newline, "int (unsigned int)") < 0) goto bad;
  __pyx_ptype_4mcdp_7context__CHandlerMeta = __Pyx_ImportType(module, "mcdp.context", "_CHandlerMeta", sizeof(struct DpHandlerMetaObject), __Pyx_ImportType_CheckSize_Warn);
   if (!__pyx_ptype_4mcdp_7context__CHandlerMeta) goto bad;
  __pyx_ptype_4mcdp_7context_Context = __Pyx_ImportType(module, "mcdp.context", "Context", sizeof(struct DpContextObject), __Pyx_ImportType_CheckSize_Warn);
   if (!__pyx_ptype_4mcdp_7context_Context) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__mcdp__context */
