# Mcdp.variable

此模块包含所有的储存变量

## `class Scoreboard`
Mcdp中的计分板类。注意，不是计分板储存型变量，因为Scoreboard没有关联实体。

### \_\_init\_\_(name,*,criteria="dummy",display=None):
初始化计分板对象
- param name(str): 计分板名称
- param criteria(str): 判据
- param display(dict | McString | None): 显示名称
- return (None): 无返回值

### apply():
应用当前计分板。只有计分板被应用，该计分板才会真正的在数据包中被创建
- return (None): 无返回值

### remove():
移除计分板
- return (None): 无返回值

### display(pos):
指定计分板的显示位置
- param pos(str): 显示位置
- return (None): 无返回值

### set_value(selector,value=0):
设置实体在计分板上的值
- param selector(str): 字符串形式的选择器
- param value(int): 设置的值
- return (None): 无返回值

### (classmethod) apply_all():
应用所有已创建和内建表中的计分板
- return (None): 无返回值

### (str) name:
计分板名称

### (str) criteria:
计分板判据

### (MCString) display_name:
显示名称

### (List[str]) \_\_class\_\_.builtins:
内建计分板名称表

### (List[str]) \_\_class\_\_.applied:
已创建并应用的计分板名称列表

### (Dict[str, Scoreboard]) \_\_class\_\_.collection:
已创建的计分板列表

## `class Score`
计分板储存型变量的基类。仅支持+=, -=, *=, /=, %=运算符。

