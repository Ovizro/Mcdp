/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE__mcdp__variable__scoreboard
#define __PYX_HAVE__mcdp__variable__scoreboard

#include "Python.h"
struct DpScoreboardObject;

/* "mcdp/variable/scoreboard.pxd":5
 * from ..context cimport DpContext_Insert
 * 
 * cdef api class Scoreboard(McdpObject) [object DpScoreboardObject, type DpScoreboard_Type]:             # <<<<<<<<<<<<<<
 *     cdef readonly:
 *         str name
 */
struct DpScoreboardObject {
  struct DpBaseObject __pyx_base;
  struct __pyx_vtabstruct_4mcdp_8variable_10scoreboard_Scoreboard *__pyx_vtab;
  PyObject *name;
  PyObject *criteria;
  struct DpStaticStrObject *display_name;
};

#ifndef __PYX_HAVE_API__mcdp__variable__scoreboard

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

#endif /* !__PYX_HAVE_API__mcdp__variable__scoreboard */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initscoreboard(void);
#else
/* WARNING: Use PyImport_AppendInittab("scoreboard", PyInit_scoreboard) instead of calling PyInit_scoreboard directly from Python 3.5 */
PyMODINIT_FUNC PyInit_scoreboard(void);

#if PY_VERSION_HEX >= 0x03050000 && (defined(__GNUC__) || defined(__clang__) || defined(_MSC_VER) || (defined(__cplusplus) && __cplusplus >= 201402L))
#if defined(__cplusplus) && __cplusplus >= 201402L
[[deprecated("Use PyImport_AppendInittab(\"scoreboard\", PyInit_scoreboard) instead of calling PyInit_scoreboard directly.")]] inline
#elif defined(__GNUC__) || defined(__clang__)
__attribute__ ((__deprecated__("Use PyImport_AppendInittab(\"scoreboard\", PyInit_scoreboard) instead of calling PyInit_scoreboard directly."), __unused__)) __inline__
#elif defined(_MSC_VER)
__declspec(deprecated("Use PyImport_AppendInittab(\"scoreboard\", PyInit_scoreboard) instead of calling PyInit_scoreboard directly.")) __inline
#endif
static PyObject* __PYX_WARN_IF_PyInit_scoreboard_INIT_CALLED(PyObject* res) {
  return res;
}
#define PyInit_scoreboard() __PYX_WARN_IF_PyInit_scoreboard_INIT_CALLED(PyInit_scoreboard())
#endif
#endif

#endif /* !__PYX_HAVE__mcdp__variable__scoreboard */
