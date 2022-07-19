#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#pragma warning(disable: 4996)

#ifdef _WIN32
#define PATH_PUBLIC __declspec(dllexport)
#endif

#include "path.h"

typedef struct stat Stat;


PATH_PUBLIC char* _fspath(const char* path, int* _len) {
	size_t len = (_len) ? *_len : 0;
	if (len == 0) {
		len = strlen(path);
	}
	if (len > PATH_MAX) {
		goto bad;
	}

	char* tmp_path = MALLOC(len + 2, char);
	if (tmp_path == NULL) {
		goto bad;
	}

	len = 0;
	for (int i = 0; i < PATH_MAX; ++i) {
		tmp_path[i] = path[i];
		if (path[i] == '\0') break;
		if (altsep && path[i] == altsep) {
			tmp_path[i] = sep;
		}
		++len;
	}
	if (tmp_path[len - 1] == sep) {
		tmp_path[len - 1] = '\0';
		len -= 1;
	}
	else {
		tmp_path[len] = '\0';
	}

	if (_len) *_len = len;
	return tmp_path;
bad:
	if (_len) *_len = 0;
	return NULL;
}

PATH_PUBLIC __inline char* _fsdir(const char* path, int* _len) {
	int len = 0;
	if (_len == NULL) _len = &len;
	char* p = _fspath(path, _len);
	if (p == NULL) return NULL;

	len = *_len;
	if (p[len - 1] != sep) {
		p[len] = sep;
		p[len + 1] = '\0';
		*_len += 1;
	}
	return p;
}

PATH_PUBLIC char* join(const char* base, const char* path) {
	int l_base = strlen(base), l_path = strlen(path);
	l_base += l_path + 1;
	char* _base = _fsdir(base, &l_base);
	char* _path = _fspath(path, &l_path);
	if (_base == NULL || _path == NULL) {
		return NULL;
	}
	strcat(_base, _path);
	FREE(_path);
	return _base;
}

PATH_PUBLIC void split(const char* _path, char** base, char** name) {
	int len = 0;
	char* path = _fspath(_path, &len);
	if (path == NULL) return;

	int i;
	for (i = len - 1; i >= 0; --i) {
		if (path[i] == sep) break;
	}

	if (name) {
		*name = MALLOC(len - i, char);
		if (*name == NULL) goto bad;
		strcpy(*name, path + i + 1);
	}

	if (base) {
		if (i < 0) {
			*base = MALLOC(2, char);
			if (*base == NULL) goto bad1;
			strcpy(*base, ".");
		}
		else {
			*base = path;
			if (i) path[i] = '\0';
			return;
		}
	}
	free(path);
	return;

bad1:
	if (name) free(*name);
bad:
	free(path);
	return;
}

PATH_PUBLIC char* dirname(const char* path) {
	char* dir = NULL;
	split(path, &dir, NULL);
	return dir;
}

PATH_PUBLIC char* basename(const char* path) {
	char* name = NULL;
	split(path, NULL, &name);
	return name;
}

PATH_PUBLIC int isabs(const char* _path) {
#ifdef _WIN32
	int len = 0;
	char* path = _fspath(_path, &len);
	if (len > 2) {
		if (path[1] == ':' && path[2] == sep) {
			char d = path[0];
			if ((d >= 'A' && d <= 'Z') || (d >= 'a' && d <= 'z')) {
				return 1;
			}
		}
		else if (path[0] == sep && path[1] == sep && path[2] != sep) {
			if (strchr(path + 3, sep)) {
				return 1;
			}
		}

	}
	return 0;
#else
	return (_path[0] == sep) ? 1 : 0;
#endif
}

PATH_PUBLIC int isexist(const char* path) {
	Stat st;
	int _sc = stat(path, &st);
	return (_sc != 0);
}

PATH_PUBLIC int isdir(const char* path) {
	Stat st;
	int _sc = stat(path, &st);
	if (_sc != 0) {
		return 0;
	}
	if S_ISDIR(st.st_mode) {
		return 1;
	}
	else
	{
		return -1;
	}
}

PATH_PUBLIC int isfile(const char* path) {
	Stat st;
	int _sc = stat(path, &st);
	if (_sc != 0) {
		return 0;
	}
	if S_ISREG(st.st_mode) {
		return 1;
	}
	else
	{
		return -1;
	}
}

PATH_PUBLIC char* abspath(const char* path) {
	if (isabs(path)) {
		return NULL;
	}
	char cwd[PATH_MAX] = { '\0' };
	GETCWD(cwd, sizeof(cwd));
	return join(cwd, path);
}

PATH_PUBLIC int rmtree(const char* path) {
	DIR* dir = opendir(path);
	if (dir == NULL) {
		return -1;
	}

	int _sc;
	for (struct dirent* next_file = readdir(dir); next_file != NULL; next_file = readdir(dir)) {
		if (strcmp(next_file->d_name, curdir) == 0 || strcmp(next_file->d_name, pardir) == 0) {
			continue;
		}
		char* p = join(path, next_file->d_name);
		if (next_file->d_type & S_IFREG) {
			_sc = remove(p);
		}
		else {
			_sc = rmtree(p);
		}
		FREE(p);
		if (_sc != 0) {
			return -3;
		}
	}
	closedir(dir);
	_sc = RMDIR(path);
	if (_sc != 0) {
		return -3;
	}
	return 0;
}

PATH_PUBLIC int copyfile(const char* src, const char* dst) {
	FILE* fr = fopen(src, "rb");
	if (fr == NULL) {
		return -1;
	}
	FILE* fw = fopen(dst, "wb");
	if (fw == NULL) {
		fclose(fr);
		return -1;
	}

	fseek(fr, 0, SEEK_END);
	int length = ftell(fr);
	char* buffer = MALLOC(length + 1, char);
	if (buffer == NULL) {
		return -2;
	}
	rewind(fr);
	fread(buffer, 1, length, fr);
	fwrite(buffer, 1, length, fw);
	FREE(buffer);

	fclose(fr);
	fclose(fw);
	return 0;
}