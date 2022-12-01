/* Generated by Cython 3.0.0a10 */

#ifndef __PYX_HAVE__mcdp__variable__mcstring
#define __PYX_HAVE__mcdp__variable__mcstring

#include "Python.h"
struct DpStrModelObject;
struct DpStrStyleObject;
struct DpStaticStrObject;

/* "mcdp/variable/mcstring.pxd":36
 * 
 * 
 * cdef api class StringModel(McdpObject) [object DpStrModelObject, type DpStrModel_Type]:             # <<<<<<<<<<<<<<
 *     cpdef dict to_dict(self)
 *     cpdef str to_json(self)
 */
struct DpStrModelObject {
  struct DpBaseObject __pyx_base;
  struct __pyx_vtabstruct_4mcdp_8variable_8mcstring_StringModel *__pyx_vtab;
};

/* "mcdp/variable/mcstring.pxd":80
 * 
 * 
 * cdef api class MCSS(StringModel) [object DpStrStyleObject, type DpStrStyle_Type]:             # <<<<<<<<<<<<<<
 *     cdef int render_flag
 *     cdef public:
 */
struct DpStrStyleObject {
  struct DpStrModelObject __pyx_base;
  int render_flag;
  PyObject *color;
  PyObject *font;
};

/* "mcdp/variable/mcstring.pxd":89
 * 
 * 
 * cdef api class BaseString(StringModel) [object DpStaticStrObject, type DpStaticStr_Type]:             # <<<<<<<<<<<<<<
 *     cdef list _extra
 *     cdef readonly MCSS style
 */
struct DpStaticStrObject {
  struct DpStrModelObject __pyx_base;
  PyObject *_extra;
  struct DpStrStyleObject *style;
  PyObject *insertion;
  struct __pyx_obj_4mcdp_8variable_8mcstring_ClickEvent *clickEvent;
  struct __pyx_obj_4mcdp_8variable_8mcstring_HoverEvent *hoverEvent;
};

#ifndef __PYX_HAVE_API__mcdp__variable__mcstring

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

#endif /* !__PYX_HAVE_API__mcdp__variable__mcstring */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initmcstring(void);
#else
/* WARNING: Use PyImport_AppendInittab("mcstring", PyInit_mcstring) instead of calling PyInit_mcstring directly from Python 3.5 */
PyMODINIT_FUNC PyInit_mcstring(void);

#if PY_VERSION_HEX >= 0x03050000 && (defined(__GNUC__) || defined(__clang__) || defined(_MSC_VER) || (defined(__cplusplus) && __cplusplus >= 201402L))
#if defined(__cplusplus) && __cplusplus >= 201402L
[[deprecated("Use PyImport_AppendInittab(\"mcstring\", PyInit_mcstring) instead of calling PyInit_mcstring directly.")]] inline
#elif defined(__GNUC__) || defined(__clang__)
__attribute__ ((__deprecated__("Use PyImport_AppendInittab(\"mcstring\", PyInit_mcstring) instead of calling PyInit_mcstring directly."), __unused__)) __inline__
#elif defined(_MSC_VER)
__declspec(deprecated("Use PyImport_AppendInittab(\"mcstring\", PyInit_mcstring) instead of calling PyInit_mcstring directly.")) __inline
#endif
static PyObject* __PYX_WARN_IF_PyInit_mcstring_INIT_CALLED(PyObject* res) {
  return res;
}
#define PyInit_mcstring() __PYX_WARN_IF_PyInit_mcstring_INIT_CALLED(PyInit_mcstring())
#endif
#endif

#endif /* !__PYX_HAVE__mcdp__variable__mcstring */
