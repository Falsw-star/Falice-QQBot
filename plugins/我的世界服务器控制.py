from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create

#要运作的函数

def 服务器查询(msg,special_content):
    message_create(msg["guild"]["id"],"1")


def loads():
    plugin_registry(name="服务器查询", usage="服务器查询",status=True)
    load_trigger(name="服务器查询", type="cmd", func=服务器查询, trigger="服务器查询", permission="all")