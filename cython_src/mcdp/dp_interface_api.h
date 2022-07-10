/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE_API__mcdp__dp_interface
#define __PYX_HAVE_API__mcdp__dp_interface
#ifdef __MINGW64__
#define MS_WIN64
#endif
#include "Python.h"
#include "dp_interface.h"

static void (*__pyx_api_f_4mcdp_12dp_interface_DpNsp_property)(char const *, T_pFactory) = 0;
#define DpNsp_property __pyx_api_f_4mcdp_12dp_interface_DpNsp_property
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


static int import_mcdp__dp_interface(void) {
  PyObject *module = 0;
  module = PyImport_ImportModule("mcdp.dp_interface");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "DpNsp_property", (void (**)(void))&__pyx_api_f_4mcdp_12dp_interface_DpNsp_property, "void (char const *, T_pFactory)") < 0) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__mcdp__dp_interface */
