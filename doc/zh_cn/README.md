# Mcdp

一个用来帮助制作数据包的Python库，  
名称"Mcdp"是"Minecraft datapack"的简称。

![Mcdp Logo](hhttps://github.com/Ovizro/Mcdp/blob/master/doc/pictures/Mcdp_logo.png)

[![License](https://img.shields.io/github/license/Ovizro/Mcdp.svg)](https://github.com/Ovizro/Mcdp/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/Mcdp.svg)](https://pypi.python.org/pypi/Mcdp)
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
[![QQ 群](https://img.shields.io/badge/QQ%E7%BE%A4-931430660-lightblue.svg)](https://jq.qq.com/?_wv=1027&k=OffuPrxM)
[![开黑啦](https://img.shields.io/badge/%E5%BC%80%E9%BB%91%E5%95%A6-25504078-blue.svg)](https://kaihei.co/cydiJJ)

> 注意！此项目目前尚未完成。

语言: [English](/doc/en_us/README.md) / 中文

## 为什么要使用它

Mcdp极大的方便了数据包的编写。诚然，现在已经有很多大佬编写出了快速创建模版，语法高亮及语法补全等非常方便的功能，但是，由于数据包本身的特性，数据包的编写依然非常复杂。  

而Mcdp则从另一个角度出发，是将Minecraft命令看作汇编语言，在此基础上进一步开发出的高级语言，提供了更多的语法抽象，为数据包的编写者带来更多的便利。同时由于Python和Minecraft命令的特点，其相对简单，易于学习，对于初学者更加友好。

或许也有人会问，如果想要更加方便的功能，为什么不去编写mod呢？
很简单，数据包与mod的定位并不是完全相同的。<br>
与mod不同，数据包是与世界绑定的。你可以为一个世界创造专有的玩法，
而不会对其他世界造成影响。<br>
同时，数据包无需Forge、Fabric等支持，你可以直接在原版中将数据包放入世界存档来使用。发送存档时，数据包会和世界存档一起打包，省去了mod安装的麻烦。<br>
数据包的兼容性也较强。Minecraft命令随版本变化较少，而且一般都是增加新的命令而已有命令保持不变。 因此只要不使用一些高版本特性，数据包很容易跨游戏版本使用而不必做出更改。

## 不适用情况 ## 

以下情况不适合使用Mcdp，或许你需要去学习一下如何制作一个mod。

1. 复杂的计算:  
   Mcdp生成的数据包的计算主要由记分板来完成。 原版命令提供的运算符较少，且计算效率低下。 虽然能够在Mcdp中通过计算实现各种数学函数，但从效率来看有些得不偿失。

2. 超出命令作用范畴:  
   Mcdp基于数据包，所有数据包无法涉及的领域Mcdp同样无法涉及。

## 工作方式 ##

Mcdp计划拥有三种工作方式: Python内部编写、由mcfzip快速创建和编译Mcdl文件。

> 这一阶段目前仅实现了Pydp[\\doge]

1. Python内部编写(Pydp)

   优点
    1. 编译快速:  
       使用Python编写不需要进行复杂的编译， 所有的编译工作基本都交予Python解释器进行。
    2. Mcdp扩展支持:  
       目前Mcdp的扩展包只能用Pydp编写。
    3. 高自由度:  
       可以与OpenCV等Python库及Vmcl解释器进行交互。
    4. 不另需编译器:  
       可以直接由Python解释器启动编译。

   缺点
    1. 操作复杂:  
       所有Mcdp函数均需要使用mcfunc装饰器。 需要的变量大多需要自行创建。 由于if/for等关键字无法捕获，需要使用相应的 上下文管理器来代替。
    2. 难以检查错误:  
       Pydp很多错误难以在编译时检查，容易导致让人困惑的行为。
       (见'Pydp常见问题')

2. 使用mcfzip(目前还没有实现)

   优点
    1. 简单便捷:  
       可以由单个文件创建整个数据包。而且基本不会出错。
       (如果命令拼错了……那就怪不得编译器了)
    2. 语法高亮兼容:  
       mcfzip的编译预处理命令是注释格式，不影响.mcfunction的语法高亮。

   缺点
    1. 功能简单:  
       简单，当然要简单到底。mcfzip只能生成含函数的数据包。 编译器只分隔命令到不同文件，不检查命令格式是否正确， 也不会对命令进行其他修改。
    2. 无扩展包:  
       mcfzip的编译不支持自定义，也没有任何可用的包。