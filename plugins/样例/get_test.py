from matcher import load_trigger, plugin_registry
from sender import ssend, get, send_message


def main(msg, special_content):
    rsp = get(msg["cid"], msg["user"]["id"],ask_content="你喜欢Falsw吗")
    send_message(msg["cid"],"你的回答是: " + str(rsp))

def loads():
    #注册插件名
    plugin_registry(name="get_test", status=False)
    load_trigger(name="get_test", type="cmd", func=main, trigger="get_test", block=False, permission="all")