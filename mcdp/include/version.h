/*
 * Mcdp version identification scheme.
 * The format of API version information is same as that of CPython API.
 */

/* Values for DP_RELEASE_LEVEL */
#define DP_RELEASE_LEVEL_ALPHA  0xA
#define DP_RELEASE_LEVEL_BETA   0xB
#define DP_RELEASE_LEVEL_GAMMA  0xC     /* For release candidates */
#define DP_RELEASE_LEVEL_FINAL  0xF     /* Serial should be 0 here */
                                        /* Higher for patch releases */

/* Version parsed out into numeric values */
/*--start constants--*/
#define DP_MAJOR_VERSION    0
#define DP_MINOR_VERSION    4
#define DP_MICRO_VERSION    0
#define DP_RELEASE_LEVEL    DP_RELEASE_LEVEL_ALPHA
#define DP_RELEASE_SERIAL   0

/* Version as a string */
#define DP_VERSION "0.4.0-Alpha"
/*--end constants--*/

/* Version as a single 4-byte hex number, e.g. 0x010502B2 == 1.5.2b2.
   Use this for numeric comparisons, e.g. #if PY_VERSION_HEX >= ... */
#define DP_VERSION_HEX ((DP_MAJOR_VERSION << 24) | \
                        (DP_MINOR_VERSION << 16) | \
                        (DP_MICRO_VERSION <<  8) | \
                        (DP_RELEASE_LEVEL <<  4) | \
                        (DP_RELEASE_SERIAL << 0))
