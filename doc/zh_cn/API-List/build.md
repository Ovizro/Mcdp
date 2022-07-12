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

### (abstractmethod) build() -> None:
抽象方法，在进入包编辑状态之前执行
- *return* (None): 无返回值 

### (abstractmethod) finalize() -> str:
抽象方法，在包结束编辑状态时执行
- *return* (str): 构建出的包的路径，应当为绝对路径

### (ClassVar[str]) `build_dir`:
构建数据包所在的文件夹，默认位置为./build
- *default*: "build"

### (bool) `remove_old_pack`:
在输出文件之前是否移除原有文件
- *default*: True

### (List[str]) `output_dir`:
包的导出目录列表。Builder会将build_dir中构建好的包复制到这些目录中。
- *default*: ['.']