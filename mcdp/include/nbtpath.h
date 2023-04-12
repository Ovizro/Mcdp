/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE__mcdp__variable__nbtpath
#define __PYX_HAVE__mcdp__variable__nbtpath

#include "Python.h"
struct DpNBTPathObject;

/* "mcdp/variable/nbtpath.pxd":12
 * 
 * 
 * cdef api class NBTPath(McdpObject) [object DpNBTPathObject, type DpNBTPath_Type]:             # <<<<<<<<<<<<<<
 *     cdef:
 *         Py_ssize_t size
 */
struct DpNBTPathObject {
  struct DpBaseObject __pyx_base;
  Py_ssize_t size;
  struct __pyx_obj_4mcdp_8variable_7nbtpath_PathNode *node;
};

#ifndef __PYX_HAVE_API__mcdp__variable__nbtpath

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#ifndef DL_IMPORT
  #define DL_IMPORT(_T) _T
#endif

#endif /* !__PYX_HAVE_API__mcdp__variable__nbtpath */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initnbtpath(void);
#else
/* WARNING: Use PyImport_AppendInittab("nbtpath", PyInit_nbtpath) instead of calling PyInit_nbtpath directly from Python 3.5 */
PyMODINIT_FUNC PyInit_nbtpath(void);

#if PY_VERSION_HEX >= 0x03050000 && (defined(__GNUC__) || defined(__clang__) || defined(_MSC_VER) || (defined(__cplusplus) && __cplusplus >= 201402L))
#if defined(__cplusplus) && __cplusplus >= 201402L
[[deprecated("Use PyImport_AppendInittab(\"nbtpath\", PyInit_nbtpath) instead of calling PyInit_nbtpath directly.")]] inline
#elif defined(__GNUC__) || defined(__clang__)
__attribute__ ((__deprecated__("Use PyImport_AppendInittab(\"nbtpath\", PyInit_nbtpath) instead of calling PyInit_nbtpath directly."), __unused__)) __inline__
#elif defined(_MSC_VER)
__declspec(deprecated("Use PyImport_AppendInittab(\"nbtpath\", PyInit_nbtpath) instead of calling PyInit_nbtpath directly.")) __inline
#endif
static PyObject* __PYX_WARN_IF_PyInit_nbtpath_INIT_CALLED(PyObject* res) {
  return res;
}
#define PyInit_nbtpath() __PYX_WARN_IF_PyInit_nbtpath_INIT_CALLED(PyInit_nbtpath())
#endif
#endif

#endif /* !__PYX_HAVE__mcdp__variable__nbtpath */