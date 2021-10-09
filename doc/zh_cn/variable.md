# Mcdp.variable

此模块包含所有的储存型变量。

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
不建议用户直接使用此类，如果想指定储存计分板名称，请使用`dp_score`。

### \_\_init\_\_(name,default=0,*,init=True,stack_offset=0,criteria="dummy",display=None):
初始化Score对象
- param name(str): 储存计分板名称
- param default(int): 变量初始值，若不进行初始化则无效
- param init(bool): 是否对变量进行初始化
- param stack_offset(int): 储存栈偏移量
- param criteria(str): 储存计分板判据
- param dispaly(dict | MCString | None): 储存计分板显示名称
- return (None): 无返回值

### set_value(value=0):
设置当前变量的值
- param value(int | Score): 新的变量值
- return (None): 无返回值

### apply():
应用当前储存计分板
- return (None): 无返回值

### (str) name: 
储存计分板名称

### (int) stack_id:
当前所在的栈层级

### (Mcdp.variable.Scoreboard) scoreboard:
储存计分板实例

## `class ScoreCache`
缓存型计分板储存变量基类，继承自Score。不建议用户直接使用，请使用下面的`dp_int`作为替代。储存计分板的名称不再能够自定义，而是自动分配。得益于这样的机制，ScoreCache的实例可以支持各种四则运算。

### \_\_init\_\_(default=0):
初始化ScoreCache实例
- param default(int | Score): 变量初始值
- return (None): 无返回值

### free():
释放该变量的占用。之后对该变量的运算会导致程序报错。
- return (None): 无返回值

### (bool) freed:
变量是否已经释放占用

## `class dp_score`
继承自Score类。在Score类型的基础上添加了类型模拟的功能，以支持Score无法支持的四则运算。

### \_\_init\_\_(name,default=0,*,init=True,stack_offset=0,criteria="dummy",display=None,simulation=None):
初始化Score对象
- param name(str): 储存计分板名称
- param default(int): 变量初始值，若不进行初始化则无效
- param init(bool): 是否对变量进行初始化
- param stack_offset(int): 储存栈偏移量
- param criteria(str): 储存计分板判据
- param dispaly(dict | MCString | None): 储存计分板显示名称
- param simulation(Type[ScoreCache] | None): 模拟类型，若为空则与Score行为相同
- return (None): 无返回值

### simulate(t_score):
设置模拟类型
- param t_score(Type[ScoreCache]): 模拟类型
- return (None): 无返回值

## `class dp_int`
继承自ScoreCache。与ScoreCache行为相同。