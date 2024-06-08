from matcher import plugin_registry, load_trigger
from sender import send_message, ssend
from matcher import PLUGINLIST

def help(msg, sc):
    if not sc:
        send_message(msg["cid"], "请用/pl看看插件吧xwx")
    else:
        global PLUGINLIST
        for plugin_name in sc:
            if plugin_name in PLUGINLIST:
                result = f"[help] - {plugin_name}"
                plugin = PLUGINLIST[plugin_name]
                if plugin["description"] or plugin["usage"]:
                    if plugin["description"]:
                        result += f"\n{plugin['description']}"
                    if plugin["usage"]:
                        result += f"\n{plugin['usage']}"
                else:
                    result += "\n(*这个插件的作者很懒，什么都没有写……)"
                ssend(msg["cid"], result)
            else:
                ssend(msg["cid"], f"没有{plugin_name}这个插件哦qaq")

def plugin(msg, sc):
    global PLUGINLIST
    result1 = "[pl] - 已经启用的插件:"
    result2 = "[pl] - 已经加载的插件:"
    for plugin_name in PLUGINLIST:
        result2 += f"\n- {plugin_name}"
        if PLUGINLIST[plugin_name]["status"]:
            result1 += f"\n- {plugin_name}"
    send_message(msg["cid"], f"{result1}\n\n{result2}")

def loads():
    plugin_registry(name="helper", description="简单的帮助插件", usage="/pl\n/help [插件名]", status=True)
    load_trigger(name="helper", type="cmd", func=help, trigger="help")
    load_trigger(name="helper", type="cmd", func=plugin, trigger="pl")
    load_trigger(name="helper", type="cmd", func=plugin, trigger="plugin")