from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from matcher import PLUGINLIST #这个字典保存着所有的插件信息
from logger import log
import os
from op import opt

#要运作的函数
def 添加(msg,special_content):
    opt(msg,'help',msg['content'][3:],"1")
def 删除(msg,special_content):
    opt(msg,'help',msg['content'][3:],"2")
def help(msg,special_content):
    opt(msg,'help')
   
def loads():
    plugin_registry(name="help", usage="/help",status=True)
    load_trigger(name="help", type="cmd", func=help, trigger="help", permission="all")
    plugin_registry(name="添加", usage="/添加",status=True)
    load_trigger(name="添加", type="cmd", func=添加, trigger="添加", permission="superusers")
    plugin_registry(name="删除", usage="/删除",status=True)
    load_trigger(name="删除", type="cmd", func=删除, trigger="删除", permission="superusers")
    