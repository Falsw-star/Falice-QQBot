from logger import log


PLUGINLIST = {}

#注册插件
def plugin_registry(name: str, discription: str = "", usage: str = "", display: bool = True, status: bool = True):
    global PLUGINLIST
    plugin = {
        "name": name,
        "status": status,
        "discription": discription,
        "usage": usage,
        "display": display,
        "triggers": {
            "services": {},
            "cmd": {},
            "keyword": {},
            "start": {},
            "end": {},
            "all": []
        }
    }
    PLUGINLIST[name] = plugin

#注册触发器
def load_trigger(name: str, type: str, func, trigger: str, block: bool = False, permission: str = "all"):
    global PLUGINLIST
    if name not in PLUGINLIST:
        log("在注册触发器时未发现相应已注册插件，请确保在插件中先注册插件再注册触发器", "WARNING")
    else:
        if type == "all":
            PLUGINLIST[name]["triggers"][type].append({
                "func" : func,
                "permission" : permission
            })
        else:
            one_trigger = {
                "block" : block,
                "permission": permission,
                "func": func
            }
            PLUGINLIST[name]["triggers"][type][trigger] = one_trigger

#匹配触发器
def match_trigger(content: str, type: str):
    global PLUGINLIST
    trigger_list = []
    for plugin_key in PLUGINLIST:
        plugin = PLUGINLIST[plugin_key]
        if plugin["status"] == True:
            if type == "cmd":
                if content in plugin["triggers"]["cmd"]:
                    log(f"插件[{plugin['name']}]的触发器[{content}](cmd)触发")
                    one_trigger = plugin["triggers"]["cmd"][content]
                    trigger_list.append(one_trigger)
            elif type == "start":
                for word in plugin["triggers"]["start"]:
                    if content.startswith(word):
                        log(f"插件[{plugin['name']}]的触发器[{word}](start)触发")
                        one_trigger = plugin["triggers"]["start"][word]
                        trigger_list.append(one_trigger)
            elif type == "end":
                for word in plugin["triggers"]["end"]:
                    if content.endswith(word):
                        log(f"插件[{plugin['name']}]的触发器[{word}](end)触发")
                        one_trigger = plugin["triggers"]["end"][word]
                        trigger_list.append(one_trigger)
            elif type == "keyword":
                for word in plugin["triggers"]["keyword"]:
                    if word in content:
                        log(f"插件[{plugin['name']}]的触发器[{word}](keyword)触发")
                        one_trigger = plugin["triggers"]["keyword"][word]
                        trigger_list.append(one_trigger)
    if trigger_list:
        return trigger_list
    else:
        return False

#匹配权限
def match_permission(user_id, permission):
    permissions = {
        "superusers": ["2123410230","2538523045"]
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
def on_cmd(user_id: str, content: str):
    cmd_symbol = "/"
    #解析结果: "triged"指示指令是否被触发，"functions"存储需要被触发的函数，"special_content"储存触发器产生的特殊消息内容（如cmd触发器的是一个保存cmd参数的列表）
    result = {
        "blocked": False,
        "functions": [],
        "special_content": None
    }
    #对消息进行处理
    arg_list = content.split()
    #判断是否属于cmd类型
    if arg_list:
        if arg_list[0].startswith(cmd_symbol):
            #产生special_content
            cmd = arg_list[0].lstrip(cmd_symbol)
            arg_list.remove(arg_list[0])
            result["special_content"] = arg_list
            if trigger_list := match_trigger(cmd,"cmd"):
                for one_trigger in trigger_list:
                    if(match_permission(user_id=user_id, permission=one_trigger["permission"])):
                        result["functions"].append(one_trigger["func"])
                        log(f"权限检查通过，准备触发({one_trigger['permission']})","SUCCESS")
                    else:
                        log(f"权限检查不通过({one_trigger['permission']})")
                    if one_trigger["block"] == True:
                        result["blocked"] = True
                        return result
    return result

#解析开头、结尾和关键字
def on_text(user_id: str, content: str):
    result = {
        "blocked": False,
        "functions": [],
        "special_content": None
    }
    if content:
        for type in ["start","end","keyword"]:
            if trigger_list := match_trigger(content,type):
                for one_trigger in trigger_list:
                    if(match_permission(user_id=user_id, permission=one_trigger["permission"])):
                        result["functions"].append(one_trigger["func"])
                        log(f"权限检查通过，准备触发({one_trigger['permission']})", "SUCCESS")
                    else:
                        log(f"权限检查不通过({one_trigger['permission']})")
                    if one_trigger["block"] == True:
                        result["blocked"] = True
                        return result
    return result

def on_all(user_id: str):
    result = {
        "blocked": False,
        "functions": [],
        "special_content": None
    }
    for plugin_key in PLUGINLIST:
        plugin = PLUGINLIST[plugin_key]
        if plugin["status"] == True:
            for one_trigger in plugin["triggers"]["all"]:
                if(match_permission(user_id=user_id, permission=one_trigger["permission"])):
                    result["functions"].append(one_trigger["func"])
                else:
                    log(f"{plugin_key}中的触发器权限不足(all)")
    return result

#主处理函数
def run(result, msg):
    for function in result["functions"]:
        function(msg, result["special_content"])
    if result["blocked"] == True:
        return True
    else:
        return False

#主匹配函数
def match(msg):
    user_id = msg["user"]["id"]
    content = msg["content"]
    run(result=on_all(user_id=user_id), msg=msg)
    if run(result=on_cmd(user_id=user_id, content=content), msg=msg):
        return
    elif run(result=on_text(user_id=user_id, content=content), msg=msg):
        return
    return

def run_services():
    global PLUGINLIST
    for plugin_key in PLUGINLIST:
        plugin = PLUGINLIST[plugin_key]
        if plugin["status"] == True:
            for service_key in plugin["triggers"]["services"]:
                function = plugin["triggers"]["services"][service_key]["func"]
                function()
