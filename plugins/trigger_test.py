from logger import log
from matcher import plugin_registry, load_trigger
from adapters.adapter_satori import message_create

def main():
    log("servicetest")

def startwith(msg,sc):
    message_create(msg["guild"]["id"],"start!")

def endwith(msg,sc):
    message_create(msg["guild"]["id"],"end!")

def keyword(msg,sc):
    message_create(msg["guild"]["id"],"keyword!")

def loads():
    plugin_registry(name="TriggerTest", status=True)
    load_trigger(name="TriggerTest",type="start",func=startwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="end",func=endwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="keyword",func=keyword,trigger="114514")