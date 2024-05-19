# Falice-QQBot
> Q:为什么叫Falice？
> A:因为很可爱!
### 简介
插件化的QQ机器人框架。

好吧，这是一个很怪的机器人，你看一下代码就懂了

耗时一天，插件目前只有一个echo

因为nonebot看不懂所以写了一个连class也没有的机器人

## 如果你想开发Falice的插件：

Falice提供了一个非常简单的插件框架。我们用echo插件做一个讲解。

```
from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create

#要运作的函数
def main(msg, special_content):
    if special_content:
        text = ""
        for arg in special_content:
            text += arg + " "
        text = text.strip()
        message_create(msg["guild"]["id"], text)

def loads():
    #注册插件名
    plugin_registry(name="echo", usage="/echo [文本]")
    #在插件名下注册触发器
    load_trigger(name="echo", type="cmd", func=main, trigger="echo", permission="not_self")
```

研究这段代码。每一个插件都有一个`loads`函数，在`loads`函数中运行从`matcher`中import的两个函数`plugin_registry`和`load_trigger`，其中`plugin_registry`要在`load_trigger`之前运作。`load_trigger`可以运行多个，以使插件拥有多个触发器。

而Falice的插件由这两部分组成：插件本体像是一个盒子，而里面装的许多触发器是真正起作用的部分。

我建议你使用vscode或者pycharm等带有纠错的编辑器编写。因为这两个函数都有必选和可选的参数。

`plugin_registry`和`load_trigger`函数的必选参数和可选参数如下：

### plugin_registry:
name: 必选，字符串类型，插件的名称。

description: 可选，字符串类型，插件描述。默认：`""`

usage: 可选，字符串类型，用法介绍。默认：`""`

display: 可选，布尔类型，预计用于隐藏插件。默认：`True`

status: 可选，布尔类型，预计用于控制插件默认的开启与关闭状态。我建议你传入一个`True`。默认：`False` 

### load_trigger:
name: 必选，字符串类型，插件名称。（这里的名字必须与上面的那个一样，否则会注册到别的插件里，或者直接报错）

type: 必选，字符串类型，触发器的类型。（目前只有cmd一类）

func: 必选，函数类型，触发器运行的函数。（当触发器被触发后，这个函数将被运行）

trigger: 可选，字符串类型，触发器将匹配该文本段的`type`形式。（比如传入`echo`，触发器将会匹配它的的`cmd`形式：`/echo`）默认：`"EMPTY"` （如果你的`type`是将来会加入的`service`类型，可以不传入该参数）

block: 可选，布尔类型，用于控制阻断。对于每条用户消息，Falice将只触发一个`type`中的触发器，而这个参数控制在该`type`内，当触发了该触发器后是否继续匹配其他触发器。默认：`False`

permission: 可选，字符串类型，控制触发器权限。目前可选的有`all`(所有人都可以触发)、`not_self`(除了自己之外的人都可以触发)、`superusers`(仅管理员可以触发)。默认：`"all"`