from logger import log
from matcher import plugin_registry, load_trigger
from adapters.adapter_satori import message_create

mn = {}

def main():
    log("servicetest")

def startwith(msg,sc):
    message_create(msg["cid"],"start!")

def endwith(msg,sc):
    message_create(msg["cid"],"end!")

def keyword(msg,sc):
    message_create(msg["cid"],"keyword!")

def all_test_show(msg,sc):
    global mn
    message_create(msg["cid"],f"从上次show以来收到了{mn[msg['guild']['id']]}条消息！")
    mn[msg["cid"]] = 0

def mn_add(msg,sc):
    global mn
    key = msg["cid"]
    if key in mn.keys():
        mn[key] += 1
    else:
        mn[key] = 0
        mn[key] += 1


def loads():
    plugin_registry(name="TriggerTest", status=True)
    load_trigger(name="TriggerTest",type="start",func=startwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="end",func=endwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="keyword",func=keyword,trigger="114514")
    load_trigger(name="TriggerTest",type="cmd",func=all_test_show,trigger="all_test_show",block=True)
    load_trigger(name="TriggerTest",type="all",func=mn_add, trigger="mn_add")