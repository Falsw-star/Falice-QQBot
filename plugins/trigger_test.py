from logger import log
from matcher import plugin_registry, load_trigger
from adapters.adapter_satori import message_create
from sender import get
def main():
    log("servicetest")

def startwith(msg,sc):
    message_create(msg['cid'],"start!")

def endwith(msg,sc):
    message_create(msg['cid'],"end!")

def keyword(msg,sc):
    message_create(msg['cid'],"keyword!")
def GET(msg,sc):
    TEXT = get(msg['cid'],msg['user']['id'],"12312313:")
    message_create(msg['cid'],TEXT)
def loads():
    plugin_registry(name="TriggerTest", status=True)
    load_trigger(name="TriggerTest",type="cmd",func=GET,trigger="191981")
    load_trigger(name="TriggerTest",type="start",func=startwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="end",func=endwith,trigger="114514",block=True)
    load_trigger(name="TriggerTest",type="keyword",func=keyword,trigger="114514")
    