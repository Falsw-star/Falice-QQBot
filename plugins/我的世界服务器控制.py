from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from mcstatus import JavaServer
from logger import log
#要运作的函数

def mc(msg,special_content):
    if msg["content"] == "mc" :
        message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n[添加]\n[删除]\n[查询]\n[开服]\n[关服]")

def states(msg,special_content):
    if msg["content"] == "状态" :
        IP = "111.161.122.206:38256"
        server = JavaServer.lookup(IP)
        try:
            server.ping
            status = server.status()        
            latency = server.ping()
            name = ' '.join(status.motd.parsed)
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n服务器名称:{name}\n服务器IP:{IP}\n服务器延时:{int(latency)}ms\n服务器版本:{status.version.name}\n在线人数:{status.players.online}")
        except:
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n连接失败")

def search(msg,special_content):
    m=msg["content"][2:].lstrip()
    
    path = "server.txt"
    


def loads():
    plugin_registry(name="mc", usage="mc",status=True)
    load_trigger(name="mc", type="start", func=mc, trigger="mc", permission="all")
    plugin_registry(name="states", usage="状态",status=True)
    load_trigger(name="states", type="start", func=states, trigger="状态", permission="all")
    plugin_registry(name="添加", usage="添加",status=True)
    load_trigger(name="添加", type="start", func=search, trigger="添加", permission="all")