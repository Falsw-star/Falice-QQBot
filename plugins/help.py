from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from matcher import PLUGINLIST #这个字典保存着所有的插件信息
from logger import log

#要运作的函数

def help(msg,special_content):
    log(PLUGINLIST,"PLUGINLIST")
    message_create(msg["guild"]["id"],"<img src='file:///F:/FBM/Falice-QQBot-main/imgs/cute.jpg'>")

def loads():
    plugin_registry(name="help", usage="/help",status=True)
    load_trigger(name="help", type="cmd", func=help, trigger="help", permission="all")