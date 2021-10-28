# Mcdp.context

此模块是低层级模块，
模块中除insert, comment, add_tag函数外，
其他函数及类不推荐直接使用。
提供了直接的文件IO操作。
用来新建文件，向文件中插入命令或注释。

## `class ContextMeta`
Context类的元类，为Context类提供上下文管理器
及初始化支持

### init(namespace):
初始化Context
- param namespace(T_Path): Context所在的命名空间
- return (None): 无返回值

### (awaitable) \_\_aenter\_\_():
创建Context运行环境

### (awaitable) \_\_aexit\_\_(exc\_type, exc\_ins, traceback):
清理静态栈并结束Context运行

### (property) top:
当前静态栈的栈顶，是一个Context实例

### (int) MAX_OPENED: 
静态栈允许的最大打开文件数，超过此数的文件会被暂时关闭

## `class Context`
处理所有mcfunction有关的文件IO。
由于元类的存在，Context的行为特殊。
其实例是一个静态栈。
通常来说，我们只需要关心Context本身，而不用

## `insert(*args)`
等价于Context.insert。向当前文件中插入一或多条命令
- param *args (str): 命令内容
- return (None): 无返回值

## `comment(*args)`
