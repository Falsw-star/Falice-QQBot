from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from matcher import PLUGINLIST #这个字典保存着所有的插件信息
from logger import log
import os
from sender import ssend

#要运作的函数
def help(msg,sc):
    if len(sc) == 0:
        name_list = []
        speak = "已加载插件\n"
        global PLUGINLIST
        for i in PLUGINLIST:
            name_list.append(i)
        name_list = sorted(name_list, key=lambda x: (len(x), x))
        for   i in name_list:
            speak += i + "\n"
        speak += "输入{/help 插件名}查看插件帮助"
        ssend(msg['cid'],speak)
        return
    else :
        if len(sc) == 1:
            try:
                ssend(msg['cid'],f"插件名:\n{sc[0]}\n使用说明:\n{PLUGINLIST[sc[0]]['usage']}")
            except:
                ssend(msg['cid'],"无此插件")
        else:
            ssend(msg['cid'],"格式错误")
def loads():
    plugin_registry(name="help", usage="{/help}获取插件列表{/help 插件名}查看插件说明",status=True)
    load_trigger(name="help", type="cmd", func=help, trigger="help", permission="all")
    