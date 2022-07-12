# Mcdp.objects

本模块为C Extension模块，包括Mcdp的基础对象——McdpObject及BaseNamespace的实现。

## `class McdpObject` 

Mcdp中所有对象的基类，提供了一套属性及方法的接口提供给未来的Vmcl编译器使用。

> 对应接口尚未被定义及使用，目前该类仅作为接口类

## `class BaseNamespace(McdpObject)`

命名空间基类，对应着数据包中的一个命名空间。该类提供了便捷的数据储存方法，可以将所有需要的与命名空间有关的数据缓存到属性中。

### (str) `n_name`:
命名空间名，该属性是只读的

### (bytes) `n_path`:
只读：命名空间路径，由于正常情况下Mcdp运行时会将工作目录切换到data中，故一般与n_name相同。为方便IO类的使用，这里使用bytes类型。该属性也是只读的

### `__init__(name: str) -> None`:
初始化命名空间
- *param* `name`(str): 命名空间名
- *return* (None): 无返回值

### (staticmethod) `property(attr: str) -> Callable[[T_Nspp_F], T_Nspp_F]`: <br>(staticmethod) `property(attr: T_Nspp_F) -> T_Nspp_F`:

在命名空间中注册一个工厂函数。提供了两种调用方式，若不提供属性名，则默认使用函数名称来注册。当第一次尝试从命名空间实例中获取`n_ + 注册名`属性时，注册的工厂函数将会被调用并将结果缓存到`__dict__`中。

- *type alias* `T_Nspp_F`: ((BaseNamespace) -> Any)
- *param* `attr`(str | T_Nspp_F): 属性注册名或工厂函数
- *return*: (((T_Nspp_F) -> T_Nspp_F) | T_Nspp_F)

用例:

```py
from mcdp.objects import BaseNamespace

@BaseNamespace.property
def newTag(nsp: BaseNamespace) -> str:
    return "DpTag_" + nsp.n_name

print(BaseNamespace("test").n_newtag)
# output: DpTag_test
```