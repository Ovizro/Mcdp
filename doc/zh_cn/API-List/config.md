# Mcdp.config

此模块包含Mcdp中所有的配置文件类及相关的函数。

## `class Config`
Mcdp的配置文件类，正常情况下，我们希望使用直接mcdp.config对象，额不是实例化该类。



## `get_config()`
获取当前的配置文件实例
- return (Config): 返回Config实例

## `check_mcdp_version(*args,eq=[],ne=[],gt=None,ge=None,lt=None,le=None)`
装饰器，使函数在定义后检查是否满足对应的Mcdp版本。  

- param args(str): 0或多个形如">0.1.2"、"==1.0"的判断表达式
- param eq(List[T_version] | T_version): 0或多个允许版本
- param ne(List[T_version] | T_version): 0或多个禁用版本
- param gt(T_version | None): 要求大于对应版本
- param ge(T_version | None): 要求大于等于对应版本
- param lt(T_version | None): 要求小于对应版本
- param le(T_version | None): 要求小于等于对应版本
- return (((*args, **kwds) -> Any) -> Any): 返回装饰器内层函数

用例:
```py
@check_mcdp_version("==1.0.0", ">0.1.0", le="0.5.2")
def func():
    """这个函数会在Mcdp版本在0.1.0到0.5.2之间或为1.0.0时执行"""
```

## `check_mc_version(*args,eq=[],ne=[],gt=None,ge=None,lt=None,le=None)`
装饰器，使函数在运行前检查是否满足对应的Minecraft版本。 
使用规则同上。