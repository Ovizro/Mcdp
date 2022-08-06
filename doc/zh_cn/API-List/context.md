# Mcdp.context

本模块为C Extension模块，提供了mcdp底层核心类Context类的实现以及相关的接口。
对用户来说，本模块最主要的作用为向函数中直接插入一段Minecraft命令或注释。

## `class Handler`
数据处理基类，用来对每行输入的数据进行处理。在mcdp核心中主要用于实现inline case。
此外，注释的添加也使用了Handler来实现。每个Handler都是一个处理节点，共同维护一个处理链。
重载该类以实现具体的处理节点。

### `__init__(next_hdl: Handler) -> None`:
初始化处理节点。

- *param* `next_hdl`(Handler): 连接的下一个处理节点
- *return* (None): 无返回值

### `do_handler(ctx: Context, code: Any) -> Any`:
实现函数，重载该方法以实现具体的数据处理。

- *param* `ctx`(Context): 当前运行环境Context实例
- *param* `code`(Any): 单行数据输入
- *return* (Any): 单行数据处理结果

用例:
```py
class TestHandler(Handler):

    def do_handler(self, ctx: Context, code: Any) -> Any:
        # We cannot ensure 'code' is a str, so please handler it yourself.
        code = "execute as @a run " + str(code)
        
        # Let next handler handle it.
        return self.next_handler(ctx, code)
```

### `next_handler(ctx: Context, code:Any) -> Any`:
相当于`self.next.do_Handler(ctx, code)`，
一般在do_handler中调用，使数据沿处理链继续传递。

- *param* `ctx`(Context): 当前运行环境Context实例
- *param* `code`(Any): 单行数据输入
- *return* (Any): 单行数据处理结果

### `append(nxt: Handler) -> None`:
向将新的处理节点添加到当前处理链的末尾

- *param* `nxt`(Handler): 新的处理节点
- *return* (None): 无返回值

### `link_to(new_head: Handler) -> Handler`:
将此处理节点添加到目标处理节点处理链的末尾并返回新的头节点，
该方法是Context添加处理节点时的默认方法。默认会继续使用目标处理节点append方法，
可以通过重载以实现链接顺序的更改。

- *param* `new_head`(Handler): 目标处理节点
- *return* (Handler): 新的头节点

### (Handler) `next`:
处理链的下个节点


## `class CommentHandler(Handler)`
注释处理节点类，在注释块中使用。

> 注意，由于`DpContext_FastComment`等底层API会绕过处理链，mcdp不保证所有的注释都会通过该处理节点

### `do_handler(ctx: Context, code: Any) -> Any`:
将输入转化为字符串并在开头加入`# `，该方法会先执行处理链再处理字符串。

- *param* `ctx`(Context): 当前运行环境Context实例
- *param* `code`(Any): 单行数据输入
- *return* (Any): 单行数据处理结果

### `link_to(new_head: Handler) -> Handler`:
将新的头节点链接到自身之后以保证注释块的正常运行。

- *param* `new_head`(Handler): 目标处理节点
- *return* (Handler): 处理节点本身

## `class Context(McdpObject)`:
context模块的核心实现类。每个Context实例对应一个mcfunction文件。
这些实例链接在一起，组成了文件栈，由于该栈只在mcdp编译器中存在，与数据包运行无关，
故也称为静态栈。静态栈的每个元素都称为一个环境。栈顶元素，也称为当前环境，
在insert等接口中获取的输入都会写入到到该环境中。

Context类则实现了相关的进栈出栈功能，以及Stream文件输出流的封装。

### `__init__(name: str, back: Context | None = ..., *, namespace: BaseNamespace | None = ..., hdl_chain: Handler | None = None)`:
初始化Context。若没有给出back参数则只会初始化部分字段。

- *param* `name`(str): 环境名称，对应未加后缀的文件名
- *param* `back`(Context | None): 要覆盖的下层环境
- *param* `namespace`(BaseNamespace | None): 环境所处的命名空间，若不存在则在设置下层环境时继承
- *param* `hdl_chain`(Handler | None): 环境添加的处理节点
- *return* (None): 无返回值

### `set_back(back: Context) -> None`:
设置Context实例对应环境的下层环境，此步完成之后才真正的完成了环境初始化。

- *param* `back`(Context): 下层环境
- *return* (None): 无返回值

### `join() -> None`:
相当于`set_back(get_context())`。

- *return* (None): 无返回值

### `activate() -> None`:
启用当前环境，将其压入栈顶作为新的当前环境。若未完全初始化则抛出McdpContextError。

- *return* (None): 无返回值

### `deactivate() -> None`:
关闭当前环境，将其从栈顶弹出并使指向的下层栈作为新的栈顶。
若当前环境不是当前实例对应的环境则抛出McdpContextError。

- *return* (None): 无返回值

### `writable() -> bool`:
检查当前实例对应环境是否可以写入

- *return* (bool): 是否可写

### `put(code: Any) -> None`:
向当前实例对应环境中写入一行内容。类型可以为任意类型，在处理链处理结束后会被转化为str。

- *param* `code`(Any): 单行内容
- *return* (None): 无返回值

### `add_handler(hdl: Handler) -> None`:
添加处理节点
