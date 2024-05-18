from logger import log


PLUGINLIST = {}

#注册插件
def plugin_registry(name: str, discription: str = "", usage: str = "", display: bool = False, status: bool = True):
    global PLUGINLIST
    plugin = {
        "name": name,
        "status": status,
        "discription": discription,
        "usage": usage,
        "display": display,
        "triggers": {
            "cmd": {},
            "keyword": {},
            "start": {},
            "end": {},
        }
    }
    PLUGINLIST[name] = plugin

#注册触发器
def load_trigger(name: str, type: str, func, trigger: str = "EMPTY", block: bool = False, permission: str = "all"):
    global PLUGINLIST
    if name not in PLUGINLIST:
        log("在注册触发器时未发现相应已注册插件，请确保在插件中先注册插件再注册触发器", "WARNING")
    else:
        one_trigger = {
            "block" : block,
            "permission": permission,
            "func": func
        }
        PLUGINLIST[name]["triggers"][type][trigger] = one_trigger

#匹配触发器
def match_trigger(trigger: str, type: str):
    global PLUGINLIST
    trigger_list = []
    for plugin_key in PLUGINLIST:
        plugin = PLUGINLIST[plugin_key]
        if plugin["status"] == True:
            if trigger in plugin["triggers"][type]:
                log(f"插件[{plugin['name']}]的触发器[{trigger}]({type})触发")
                one_trigger = plugin["triggers"][type][trigger]
                if one_trigger["block"] == True:
                    return [one_trigger]
                else:
                    trigger_list.append(one_trigger)
    if trigger_list:
        return trigger_list
    else:
        return False

#匹配权限
def match_permission(user_id, permission):
    permissions = {
        "superusers": ["3435578673","2538523045"]
    }
    if permission == "all":
        return True
    elif permission == "not_self":
        from adapters.adapter_satori import LOGIN
        if user_id == LOGIN["id"]:
            return False
        else:
            return True
    elif user_id in permissions[permission]:
        return True
    else:
        return False

#解析cmd
def on_cmd(user_id:str, content: str):
    cmd_symbol = "/"
    #解析结果: "triged"指示指令是否被触发，"functions"存储需要被触发的函数，"special_content"储存触发器产生的特殊消息内容（如cmd触发器的是一个保存cmd参数的列表）
    result = {
        "triged": False,
        "functions": [],
        "special_content": None
    }
    #对消息进行处理
    arg_list = content.split()
    #判断是否属于cmd类型
    if arg_list[0].startswith(cmd_symbol):
        #产生
        cmd = arg_list[0].lstrip(cmd_symbol)
        arg_list.remove(arg_list[0])
        result["special_content"] = arg_list
        if trigger_list := match_trigger(cmd,"cmd"):
            for one_trigger in trigger_list:
                result["triged"] = True
                if(match_permission(user_id, one_trigger["permission"])):
                    result["functions"].append(one_trigger["func"])
                    log(f"权限检查通过，准备触发({one_trigger['permission']})","SUCCESS")
                else:
                    log(f"权限检查不通过({one_trigger['permission']})")
    return result

#主处理函数
def run(result, msg):
    if result["triged"] == True:
        for function in result["functions"]:
            function(msg, result["special_content"])
        return True
    else:
        return False

#主匹配函数
def match(msg):
    user_id = msg["user"]["id"]
    content = msg["content"]
    result = on_cmd(user_id=user_id, content=content)
    if run(result=result, msg=msg):
        return