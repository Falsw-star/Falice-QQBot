from sender import send_message
from matcher import plugin_registry, load_trigger
from mcstatus import JavaServer

def mcs(msg, sc):
    if sc:
        result = "[MCStatus]: 你的服务器qwq"
        for server_ip in sc:
            try:
                server = JavaServer.lookup(server_ip)
                status = server.status()
                latency = server.ping()
                rsp = "服务器IP: " + server_ip + "\n" + "在线人数: " + str(status.players.online) + "\n" + "Ping: " + str(round(latency)) + "\n" + "服务器版本: " + status.version.name
            except Exception as e:
                rsp = f"服务器关闭或不存在:\n[{e}]"
            result += f"\n{rsp}"
        send_message(msg["cid"], rsp)
    else:
        send_message(msg["cid"], "[MCStatus] 请输入服务器ip")

def loads():
    plugin_registry(name="MCStatus", description="基于mcstatus的服务器查看(目前仅Java版)", usage="/mcs [服务器ip] [服务器ip] ...", status=True)
    load_trigger(name="MCStatus", type="cmd", func=mcs, trigger="mcs", block=False, permission="all")