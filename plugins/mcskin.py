from matcher import plugin_registry, load_trigger
from sender import send_message
import json
import requests
import base64

def littleskin(name):
    try:
        rsp = json.loads(requests.get("https://littleskin.cn/csl/" + name + ".json", timeout = 5).text)['skins']
        if('slim' in rsp.keys()):
            return "https://littleskin.cn/textures/" + rsp['slim']
        elif('default' in rsp.keys()):
            return "https://littleskin.cn/textures/" + rsp['default']
        else:
            return "ERROR"
    except Exception as e:
        return "ERROR"

def mojang(name):
    try:
        rsp = json.loads(requests.get("https://api.mojang.com/users/profiles/minecraft/" + name, timeout = 5).text)
        if('errorMessage' in rsp.keys()):
            return rsp['erroeMessage']
        elif('id' in rsp.keys()):
            rsp = json.loads(requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + rsp['id'], timeout = 5).text)
            dc = rsp['properties'][0]['value']
            dc = json.loads(base64.b64decode(dc))
            return dc['textures']['SKIN']['url']
        else:
            return "ERROR"
    except Exception as e:
        return "ERROR"

def skin(msg, sc):
    if len(sc) != 1:
        send_message(msg["cid"], "参数错误")
        return
    else:
        mojang_skin = mojang(sc[0])
        if mojang_skin != "ERROR":
            mojang_skin = f"<img src='{mojang_skin}'/>\n{mojang_skin}"
        littleskin_skin = littleskin(sc[0])
        if littleskin_skin != "ERROR":
            littleskin_skin = f"<img src='{littleskin_skin}'/>\n{littleskin_skin}"
        result = f"Mojang:\n{mojang_skin}\n\nLittleSkin:\n{littleskin_skin}"
        send_message(msg["cid"], result)

def loads():
    plugin_registry(name="mcskin", discription="获取MC皮肤", usage="{/skin 玩家名}获取皮肤站皮肤", status=True)
    load_trigger(name="mcskin", type="cmd", func=skin, trigger="skin", permission="all")