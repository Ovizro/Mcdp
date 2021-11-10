# 快速开始

这是一个简短的教程来帮助你快速入门

> 由于该项目目前正在开发，该文档可能会随时更改。里面的内容也可能因为文档更新的延误而暂时无法使用，还请见谅。

## 前期准备

想要玩转Mcdp这个Python库，我们需要准备两个东西——Minecraft和Python。  

Minecraft自然不用多说，只要是>=1.14的JE版就没有问题。
同时，我们需要在电脑上安装一个Python。推荐使用3.8或以上的版本，否则可能会出现兼容问题。

> 嗯，什么是Python？Python是一种计算机程序设计语言。基础的Python安装教程可以参考[这里](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)

光有一个Python本体还不行，我们还需要到[Github](https://github.com/Ovizro/Mcdp/releases)中下载最新的Mcdp包。
[![在这里下载](https://github.com/Ovizro/Mcdp/blob/master/doc/pictures/Mcdp_releases.png)](https://github.com/Ovizro/Mcdp/releases)

最后在你下载下来的包所在的文件夹中打开控制台，输入以下命令来进行安装，以0.1.0版本为例。

    pip install Mcdp-0.1.0.tar.gz

> 一个方便的打开控制台的办法是在文件夹中按住shift点右键->在此处打开powershell

## 开始使用

那么，按照惯例，我们先来一个"Hello world"。
新建一个test_mcdp.py，然后输入以下内容。

```py
from mcdp import *

Config("MyFirstDatapack", "1.16.5", "Hello world!")

@mcfunc_main
def main():
    add_tag("minecraft:load")
    cout << "Hello world!" << endl
```

如果你已经成功的完成了安装步骤，在运行过后，test_mcdp.py所在的文件夹中就会多出一个名为MyFirstDatapack的文件夹，这个就是一个完整的数据包啦。
然后，把这个文件夹复制到世界存档的datapacks文件夹中，进入游戏。输入`/reload`命令进行一下重载。如果你能看到聊天框中的"Hello world!"，就说明你成功了。

## 