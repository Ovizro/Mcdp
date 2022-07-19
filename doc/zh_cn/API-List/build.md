# Mcdp.build

该模块主要提供Mcdp构建数据包基础目录结构的接口。

## 使用类型
- `mcdp.version.T_version`: Version | Tuple[str | int, ...] | Dict[str, str | int] | str

## `class PackageInformation(pydantic.BaseModel)`
包信息记录类，记录一个包的基础信息。

### (str) `name`:
数据包名称

### (mcdp.version.Version) `support_version`:
数据包支持的Minecraft版本

### (str) `description`:
数据包的描述

### (str | os.Pathlike | None) `icon_path`:
数据包图标的路径

## `class AbstractBuilder(PackageInfomation)`
Mcdp构建器抽象基类，提供相关接口及上下文管理器供上层调用

### (abstractmethod) `build() -> None`:
抽象方法，在进入包编辑状态之前执行
- *return* (None): 无返回值 

### (abstractmethod) `finalize() -> str`:
抽象方法，在包结束编辑状态时执行
- *return* (str): 构建出的包的路径，应当为绝对路径

### `__enter__() -> AbstractBuilder`:
上下文管理器处理函数，build函数在这一步执行
- *return* (AbstractBuilder): 返回实例本身

### `__exit__(*args) -> None`:
上下文管理器处理函数，finalize函数在这一步执行
- *return* (None): 无返回值 

### (ClassVar[str]) `build_dir`:
构建数据包所在的文件夹，默认位置为./build
- *value*: "build"

### (bool) `remove_old_pack`:
在输出文件之前是否移除原有文件
- *default*: True

### (List[str]) `output_dir`:
包的导出目录列表。Builder会将build_dir中构建好的包复制到这些目录中。
- *default*: ['.']


## `class PackBuilder(AbstractBuilder)`
Minecraft包构建基类，提供了一个Minecraft包的构建模版。

### `build() -> None`:
建立如下的文件结构
```
<name>  
│  pack.mcmeta
│
└─<src_dir>
```
- *return* (None): 无返回值 

### `finalize() -> str`:
对包文件夹进行可选的打包，若make_archive为true，则将包打包为zip格式
- *return* (str): 包文件夹路径或zip文件路径

### `get_mcmeta() -> Dict[str, Any]`:
pack.mcmeta中的数据，格式为
```json
{
    "pack": {
        "pack_format": "<pack_format>",
        "description": "<description>"
    }
}
```
- *return* (Dict[str, Any]): mcmeta数据

### (abstractmethod) `get_pack_format() -> int`:
获取support_version对应的pack_format
- *return* (int): 版本号数据

### (ClassVar[str]) `src_dir`:
构建的数据文件夹名

### (bool) `make_archive`:
是否打包为zip

## `class DatapackBuilder(PackBuilder)`:

### (abstractmethod) `get_pack_format() -> int`:
获取support_version对应的数据包版本号

> 这里的版本号参考[Minecraft Wiki](https://minecraft.fandom.com/zh/wiki/%E6%95%B0%E6%8D%AE%E5%8C%85#%E6%95%B0%E6%8D%AE%E5%8C%85%E7%89%88%E6%9C%AC)

- *return* (int): 版本号数据

### (ClassVar[str]) `src_dir`:
构建的数据文件夹名
- *value*: "data"

## `get_defaultbuilder() -> Type[AbstractBuilder]`:
获取默认的构建器
- *return* (Type[AbstractBuilder]): 默认构建器

## `set_defaultbuilder(builder: Type[AbstractBuilder]) -> None`:
将对应的构建器类设置为默认构建器
- *param* `builder`(Type[AbstractBuilder]): 默认构建器
- *return* (None): 无返回值