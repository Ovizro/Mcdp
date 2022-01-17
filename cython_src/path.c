#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <direct.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>

#pragma warning(disable: 4996)

#define MALLOC(size, type) (type*)malloc((size) * sizeof(type))
#define FREE free

#ifdef  _MSC_VER
#define PATH_PUBLIC __declspec(dllexport)
#else
#define PATH_PUBLIC
#endif //  _MSC_VER


typedef struct stat Stat;

PATH_PUBLIC char* _fspath(const char* path) {
	size_t len = strlen(path);
	char* tmp_path = MALLOC(len + 1, char);
	if (tmp_path == NULL) {
		return NULL;
	}
	for (int i = 0; i < len; ++i) {
		if (path[i] == '/') {
			tmp_path[i] = '\\';
		}
		else
		{
			tmp_path[i] = path[i];
		}
	}
	if (tmp_path[len - 1] == '\\') {
		tmp_path[len - 1] = '\0';
	}
	else
	{
		tmp_path[len] = '\0';
	}
	return tmp_path;
}

char* _join_path(const char* base, const char* path) {
	size_t len0 = strlen(base);
	size_t len1 = strlen(path);
	size_t len = len0 + len1 + 1;
	char* buffer = MALLOC(len + 1, char);
	if (buffer == NULL) {
		return NULL;
	}

	strcpy(buffer, base);
	buffer[len0] = '\\';
	buffer[len0 + 1] = '\0';

	strcat(buffer, path);
	buffer[len] = '\0';
	return buffer;
}

PATH_PUBLIC char* join_path(const char* base, const char* path) {
	char* _base = _fspath(base);
	char* _path = _fspath(path);
	if (_base == NULL || _path == NULL) {
		return NULL;
	}
	char* new_p = _join_path(_base, _path);
	FREE(_base);
	FREE(_path);
	return new_p;
}

PATH_PUBLIC void split(const char* path, char** base, char** name) {
	size_t len = strlen(path);
	int i;
	for (i = len - 1; i >= 0; --i) {
		if (path[i] == '\\') {
			break;
		}
	}
	if (i < 0) {
		if (name != NULL) {
			*name = MALLOC(len + 1, char);
			if (*name == NULL) {
				return;
			}
			strcpy(*name, path);
		}
		if (base != NULL) {
			*base = MALLOC(3, char);
			if (*base == NULL) {
				return;
			}
			strcpy(*base, ".");
		}
	}
	else if (i == 0)
	{
		if (name != NULL) {
			*name = MALLOC(len, char);
			if (*name == NULL) {
				return;
			}
			strcpy(*name, path + 1);
		}
		if (base != NULL) {
			*base = MALLOC(3, char);
			if (*base == NULL) {
				return;
			}
			strcpy(*base, "/.");
		}
	}
	else
	{
		if (base != NULL) {
			*base = MALLOC(i + 1, char);
			if (*base == NULL) {
				return;
			}
			strncpy(*base, path, i);
		}
		if (name != NULL) {
			*name = MALLOC(len - i + 1, char);
			if (*name == NULL) {
				return;
			}
			strcpy(*name, path + i + 1);

		}
	}
}

PATH_PUBLIC char* dirname(const char* path) {
	char* dir = NULL;
	char* tmp_path = _fspath(path);
	if (tmp_path == NULL) {
		return NULL;
	}
	split(tmp_path, &dir, NULL);
	FREE(tmp_path);
	return dir;
}

PATH_PUBLIC char* basename(const char* path) {
	char* name = NULL;
	char* tmp_path = _fspath(path);
	if (tmp_path == NULL) {
		return NULL;
	}
	split(tmp_path, NULL, &name);
	FREE(tmp_path);
	return name;
}

int _isabs(const char* path) {
	size_t len = strlen(path);
	if (len > 1) {
		if (path[1] == ':') {
			char d = path[0];
			if ((d >= 'A' && d <= 'Z') || (d >= 'a' && d <= 'z')) {
				return 1;
			}
		}
	}
	return 0;
}

PATH_PUBLIC int isabs(const char* path) {
	char* tmp_path = _fspath(path);
	if (tmp_path == NULL) {
		return -1;
	}
	int b = _isabs(tmp_path);
	FREE(tmp_path);
	return b;
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
	_getcwd(cwd, sizeof(cwd));
	return join_path(cwd, path);
}

int _rmtree(const char* path) {
	DIR* dir;
	int _sc;

	int len = strlen(path);
	if (path[len - 1] != '/' && path[len - 1] != '\\') {
		char* tmp_path = MALLOC(len + 2, char);
		if (tmp_path == NULL) {
			return -2;
		}
		strcpy(tmp_path, path);
		tmp_path[len] = '\\';
		tmp_path[len + 1] = '\0';
		dir = opendir(tmp_path);
		FREE(tmp_path);
	}
	else
	{
		dir = opendir(path);
	}

	if (dir == NULL) {
		return -1;
	}
	for (struct dirent* next_file = readdir(dir); next_file != NULL; next_file = readdir(dir)) {
		if (strcmp(next_file->d_name, ".") == 0 || strcmp(next_file->d_name, "..") == 0) {
			continue;
		}
		char* p = _join_path(path, next_file->d_name);
		if (next_file->d_type & S_IFREG) {
			_sc = remove(p);
		}
		else
		{
			_sc = _rmtree(p);
		}
		FREE(p);
		if (_sc != 0) {
			return -3;
		}
	}
	closedir(dir);
	_sc = _rmdir(path);
	if (_sc != 0) {
		return -2;
	}
	return 0;
}

PATH_PUBLIC int rmtree(const char* path) {
	char* tmp_path = _fspath(path);
	if (tmp_path == NULL) {
		return -2;
	}
	int _sc = _rmtree(tmp_path);
	FREE(tmp_path);
	return _sc;
}

PATH_PUBLIC int copyfile(const char* src, const char* dst) {
	char* _src = _fspath(src);
	char* _dst = _fspath(dst);
	if (_src == NULL || _dst == NULL) {
		return -2;
	}

	FILE* fr = fopen(_src, "rb");
	FREE(_src);
	if (fr == NULL) {
		return -1;
	}
	FILE* fw = fopen(_dst, "wb");
	FREE(_dst);
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