from matcher import plugin_registry, load_trigger
from sender import send_message, guild_list, friend_list
import json

from matcher import PLUGINLIST

def enable(msg, sc):
    if len(sc) == 1:
        plugin_name = sc[0]
        group = [msg["cid"]]
    elif len(sc) == 2:
        plugin_name = sc[0]
        group = [sc[1]]
    if plugin_name not in PLUGINLIST:
        send_message(msg["cid"], "[PM] 插件不存在")
        return
    if group[0] == "all":
        group = []
        groups = json.loads(guild_list())
        for guild in groups["data"]:
            group.append(guild["id"])
        friends = json.loads(friend_list())
        for friend in friends["data"]:
            group.append(f"private:{friend['id']}")
    rsp_text = "启用:"
    for id in group:
        PLUGINLIST[plugin_name]["status"][id] = True
        rsp_text += f"\n- {plugin_name}"
    send_message(msg["cid"], rsp_text)

def disable(msg, sc):
    if len(sc) == 1:
        plugin_name = sc[0]
        group = [msg["cid"]]
    elif len(sc) == 2:
        plugin_name = sc[0]
        group = [sc[1]]
    if plugin_name not in PLUGINLIST:
        send_message(msg["cid"], "[PM] 插件不存在")
        return
    if group[0] == "all":
        group = []
        groups = json.loads(guild_list())
        for guild in groups["data"]:
            group.append(guild["id"])
        friends = json.loads(friend_list())
        for friend in friends["data"]:
            group.append(f"private:{friend['id']}")
    rsp_text = "禁用:"
    for id in group:
        PLUGINLIST[plugin_name]["status"][id] = False
        rsp_text += f"\n- {plugin_name}"
    send_message(msg["cid"],rsp_text)

def loads():
    plugin_registry(name="PluginManager", usage="/enable [插件名] [群号]\n/disable [插件名] [群号]\n群号默认为消息收到的channelid all为所有的聊天")
    load_trigger(name="PluginManager", type="cmd", func=enable, trigger="enable", block=True)
    load_trigger(name="PluginManager", type="cmd", func=disable, trigger="disable", block=True)