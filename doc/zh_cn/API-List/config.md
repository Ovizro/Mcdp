# Mcdp.config

此模块包含Mcdp中所有的配置文件类及相关的函数。

## `class Config`
Mcdp的总体配置文件类，需要在Mcdp运行之前配置完毕

### \_\_init\_\_(name,version,description,*,namespace,icon_path)：  
初始化配置文件
- param name(str): 数据包名称
- param version(T_version): 适配的MC版本，如'1.16.3'
- param description(str): 数据包的描述文本
- param namespace(str | None): 命名空间名称，默认使用数据包名
- param icon_path(str | os.Pathlike | None): 图标路径，可选
- return (None): 无返回值 

### (str) name:
数据包名称

### (Mcdp.version.Version) version:
当前支持的Minecraft版本

### (str) description:
数据包的描述

### (str | os.Pathlike | None) icon_path:
数据包图标的路径

### (str) namespace:
命名空间名称

## `get_config()`
获取当前的配置文件实例
- return (Config): 返回Config实例

## `check_mcdp_version(*args,eq=[],ne=[],gt=None,ge=None,lt=None,le=None)`
装饰器，使函数在定义后检查是否满足对应的Mcdp版本。  
使用示例如下
```py
@check_mcdp_version("==1.0.0", ">0.1.0", le="0.5.2")
def func():
    """这个函数会在Mcdp版本在0.1.0到0.5.2之间或为1.0.0时执行"""
    ...
```
- param args(str): 0或多个形如">0.1.2"、"==1.0"的判断表达式
- param eq(List[T_version] | T_version): 0或多个允许版本
- param ne(List[T_version] | T_version): 0或多个禁用版本
- param gt(T_version | None): 要求大于对应版本
- param ge(T_version | None): 要求大于等于对应版本
- param lt(T_version | None): 要求小于对应版本
- param le(T_version | None): 要求小于等于对应版本
- return ((*args, **kwds) -> Any) -> Any: 返回装饰器内层函数

## `check_mc_version(*args,eq=[],ne=[],gt=None,ge=None,lt=None,le=None)`
装饰器，使函数在运行前检查是否满足对应的Minecraft版本。 
使用规则同上，不再赘述。

## `get_version(mc_version)`
将Minecraft版本转化为数据包版本号
- param mc_version(T_version): MC版本
- return (int): 数据包版本号