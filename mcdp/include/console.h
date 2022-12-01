/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE__mcdp__variable__console
#define __PYX_HAVE__mcdp__variable__console

#include "Python.h"

/* "mcdp/variable/console.pxd":7
 * 
 * 
 * cdef api enum MCTitle_TypeFlag:             # <<<<<<<<<<<<<<
 *     TITLE
 *     SUBTITLE
 */
enum MCTitle_TypeFlag {
  TITLE,
  SUBTITLE,
  ACTIONBAR
};

#ifndef __PYX_HAVE_API__mcdp__variable__console

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

#endif /* !__PYX_HAVE_API__mcdp__variable__console */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initconsole(void);
#else
/* WARNING: Use PyImport_AppendInittab("console", PyInit_console) instead of calling PyInit_console directly from Python 3.5 */
PyMODINIT_FUNC PyInit_console(void);

#if PY_VERSION_HEX >= 0x03050000 && (defined(__GNUC__) || defined(__clang__) || defined(_MSC_VER) || (defined(__cplusplus) && __cplusplus >= 201402L))
#if defined(__cplusplus) && __cplusplus >= 201402L
[[deprecated("Use PyImport_AppendInittab(\"console\", PyInit_console) instead of calling PyInit_console directly.")]] inline
#elif defined(__GNUC__) || defined(__clang__)
__attribute__ ((__deprecated__("Use PyImport_AppendInittab(\"console\", PyInit_console) instead of calling PyInit_console directly."), __unused__)) __inline__
#elif defined(_MSC_VER)
__declspec(deprecated("Use PyImport_AppendInittab(\"console\", PyInit_console) instead of calling PyInit_console directly.")) __inline
#endif
static PyObject* __PYX_WARN_IF_PyInit_console_INIT_CALLED(PyObject* res) {
  return res;
}
#define PyInit_console() __PYX_WARN_IF_PyInit_console_INIT_CALLED(PyInit_console())
#endif
#endif

#endif /* !__PYX_HAVE__mcdp__variable__console */
