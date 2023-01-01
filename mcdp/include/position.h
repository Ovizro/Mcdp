/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE__mcdp__variable__position
#define __PYX_HAVE__mcdp__variable__position

#include "Python.h"
struct DpComponentObject;
struct DpPositionObject;

/* "mcdp/variable/position.pxd":6
 * 
 * 
 * cdef api enum MCPos_TypeFlag:             # <<<<<<<<<<<<<<
 *     NANTYPE = 0
 *     LOCAL_POSITION
 */
enum MCPos_TypeFlag {
  NANTYPE = 0,
  LOCAL_POSITION,
  ABSOLUTE_POSITION,
  RELATIVE_POSITION
};

/* "mcdp/variable/position.pxd":16
 * 
 * 
 * cdef api class Component(McdpObject) [object DpComponentObject, type DpComponent_Type]:             # <<<<<<<<<<<<<<
 *     cdef:
 *         str raw_value
 */
struct DpComponentObject {
  struct DpBaseObject __pyx_base;
  struct __pyx_vtabstruct_4mcdp_8variable_8position_Component *__pyx_vtab;
  PyObject *raw_value;
  enum MCPos_TypeFlag type_flag;
  float offset;
};

/* "mcdp/variable/position.pxd":26
 * 
 * 
 * cdef api class Position(McdpObject) [object DpPositionObject, type DpPosition_Type]:             # <<<<<<<<<<<<<<
 *     cdef MCPos_TypeFlag type_flag
 *     cdef readonly:
 */
struct DpPositionObject {
  struct DpBaseObject __pyx_base;
  struct __pyx_vtabstruct_4mcdp_8variable_8position_Position *__pyx_vtab;
  enum MCPos_TypeFlag type_flag;
  PyObject *components;
};

#ifndef __PYX_HAVE_API__mcdp__variable__position

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

#endif /* !__PYX_HAVE_API__mcdp__variable__position */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initposition(void);
#else
/* WARNING: Use PyImport_AppendInittab("position", PyInit_position) instead of calling PyInit_position directly from Python 3.5 */
PyMODINIT_FUNC PyInit_position(void);

#if PY_VERSION_HEX >= 0x03050000 && (defined(__GNUC__) || defined(__clang__) || defined(_MSC_VER) || (defined(__cplusplus) && __cplusplus >= 201402L))
#if defined(__cplusplus) && __cplusplus >= 201402L
[[deprecated("Use PyImport_AppendInittab(\"position\", PyInit_position) instead of calling PyInit_position directly.")]] inline
#elif defined(__GNUC__) || defined(__clang__)
__attribute__ ((__deprecated__("Use PyImport_AppendInittab(\"position\", PyInit_position) instead of calling PyInit_position directly."), __unused__)) __inline__
#elif defined(_MSC_VER)
__declspec(deprecated("Use PyImport_AppendInittab(\"position\", PyInit_position) instead of calling PyInit_position directly.")) __inline
#endif
static PyObject* __PYX_WARN_IF_PyInit_position_INIT_CALLED(PyObject* res) {
  return res;
}
#define PyInit_position() __PYX_WARN_IF_PyInit_position_INIT_CALLED(PyInit_position())
#endif
#endif

#endif /* !__PYX_HAVE__mcdp__variable__position */
