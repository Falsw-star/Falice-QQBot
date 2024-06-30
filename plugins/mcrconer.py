import mcrcon
from matcher import plugin_registry, load_trigger
from sender import send_message, get
from plugins.mcserver.server import Server
import time

SERVERS = {}

def rcon(msg, sc):
    select = {}
    select_message = "[Falmcsm Rconer]\n选择本次要操作的服务器吧！\n"
    i = 1
    for a in SERVERS:
        select[str(i)] = a
        select_message += f"\n{i}. {a}"
        i += 1
    select_message += "\n\n输入序号选择服务器: (30s)"
    n = get(msg["cid"], msg["user"]["id"], select_message, timeout=30, timeout_rsp=False)
    if n is None:
        send_message(msg["cid"], "[Falmcsm Rconer] 那我就睡觉去啦……")
        return
    if n not in select:
        send_message(msg["cid"], "[Falmcsm Rconer] 嗯……没有这个呢……(zzzz)")
        return
    server = SERVERS[select[n]]
    send_message(msg["cid"], "[Falmcsm Rconer] 已进入服务器控制模式! 请根据提示键入指令: (114514s)")
    while True:
        pannel = f"[控制面板]\n你正在控制 {server.Server_Name} :\n"
        if server.status == -1:
            pannel += "该服务器处于离线状态。\n\n"
        elif server.status == 0:
            pannel += "该服务器正在启动……请稍后……\n\n"
        elif server.status == 1:
            pannel += f"该服务器在线。\n{server.call('list')[0]}\n\n"
        pannel += "start - 启动服务器\nstop - 停止服务器\ncmd - 发送指令\ninfo - 获取服务器信息\n[other] - 重复本菜单\n\nexit - 退出控制模式"
        rsp = get(msg["cid"], msg["user"]["id"], pannel, timeout=114514, timeout_rsp=False)
        if rsp is None:
            break
        if rsp == "start":
            if server.status == -1:
                send_message(msg["cid"], "[Falmcsm Rconer] 启动中……")
                if(server.start()):
                    send_message(msg["cid"], "[Falmcsm Rconer] 启动成功！")
                else:
                    send_message(msg["cid"], "[Falmcsm Rconer] 启动失败！")
            else:
                send_message(msg["cid"], "[Falmcsm Rconer] 该服务器暂时无法启动。")
        if rsp == "stop":
            if server.status == 1:
                send_message(msg["cid"], "[Falmcsm Rconer] 停止中……")
                server.call("stop")
                while True:
                    if server.status == -1:
                        send_message(msg["cid"], "[Falmcsm Rconer] 停止成功！")
                        break
                    time.sleep(1)
            else:
               send_message(msg["cid"], "[Falmcsm Rconer] 停 止 不 能")
        if rsp == "cmd":
            if server.status == 1:
                command = get(msg["cid"], msg["user"]["id"], "要运行的指令: (30s)", timeout=30, timeout_rsp=False)
                if command is None:
                    continue
                server_rsp = f"运行的指令: {command}\n\n{str(server.call(command)[0])}"
                if len(server_rsp) > 1997:
                    server_rsp = server_rsp[:1997] + "..."
                send_message(msg["cid"], server_rsp)
            else:
                send_message(msg["cid"], "[Falmcsm Rconer] 操 作 不 能")
        if rsp == "info":
            pass
        if rsp == "exit":
            break
        time.sleep(3)
    send_message(msg["cid"], "[Falmcsm Rconer] 已退出控制模式。")


def loads():
    plugin_registry(name="MCRconer", description="我的世界服务器管理插件", usage="/rcon", status=False)
    load_trigger(name="MCRconer", type="cmd", func=rcon, trigger="rcon", permission="superusers")