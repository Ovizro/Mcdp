#ifndef _INCLUDE_PATH_
#define _INCLUDE_PATH_

#define MALLOC(size, type) (type*)malloc((size) * sizeof(type))
#define FREE free

#ifdef _WIN32
#include "dirent.h"
#include <direct.h>

#define MKDIR(path, mode) _mkdir(path)
#define CHDIR _chdir
#define GETCWD _getcwd
#define RMDIR _rmdir
#ifndef PATH_PUBLIC
#define PATH_PUBLIC __declspec(dllimport)
#endif // !PATH_PUBLIC

static const char const extsep = '.';
static const char const sep = '\\';
static const char const pathsep = ';';
static const char const altsep = '/';

static const char* const curdir = ".";
static const char* const pardir = "..";
static const char* const defpath = ".;C:\\bin";
static const char* const devnull = "nul";
#else
#define _POSIX_C_SOURCE 1
#include <unistd.h>
#include <dirent.h>

#define MKDIR(path, mode) mkdir(path, mode)
#define CHDIR chdir
#define GETCWD getcwd
#define RMDIR rmdir
#define PATH_PUBLIC
#ifndef PATH_PUBLIC
#define PATH_PUBLIC
#endif // !PATH_PUBLIC

#ifndef PATH_MAX
#define PATH_MAX 1024
#endif

static const char const extsep = '.';
static const char const sep = '/';
static const char const pathsep = ';';
static const char const altsep = 0;

static const char* const curdir = ".";
static const char* const pardir = "..";
static const char* const defpath = "/bin:/usr/bin";
static const char* const devnull = "/dev/null";
#endif //  WIN32

#define fspath(path) _fspath(path, NULL)
#define fsdir(path) _fsdir(path, NULL)


#ifdef __cplusplus
extern "C" {
#endif

PATH_PUBLIC char* _fspath(const char* path, int* len);
PATH_PUBLIC char* _fsdir(const char* path, int* len);
PATH_PUBLIC char* join(const char* base, const char* path);
PATH_PUBLIC void split(const char* _path, char** base, char** name);
PATH_PUBLIC char* dirname(const char* path);
PATH_PUBLIC char* basename(const char* path);

PATH_PUBLIC int isabs(const char* _path);
PATH_PUBLIC int isexist(const char* path);
PATH_PUBLIC int isdir(const char* path);
PATH_PUBLIC int isfile(const char* path);
PATH_PUBLIC char* abspath(const char* path);
PATH_PUBLIC int rmtree(const char* path);
PATH_PUBLIC int copyfile(const char* src, const char* dst);

#ifdef __cplusplus
}
#endif

#endif // !_INCLUDE_PATH_