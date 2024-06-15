from matcher import plugin_registry, load_trigger
from sender import ssend, get, send_message
from db import database
import time
from logger import log
from copy import deepcopy
import importlib
import re

def regex_match(s, pattern: str):
    return bool(re.search(pattern, s))

def item_append(name: str, item: dict, location: list):
    db = database("WTE_world")
    db.open()
    place = db.data
    for key in location:
        place = place[key]
    if name not in place:
        place[name] = item
        db.save()
    else:
        n = 1
        while True:
            if (name + str(n)) not in place:
                name = name + "-" + str(n)
                place[name] = item
                db.save()
                break
            n += 1
    if item["WTE_ITEM_INFO"]["type"] == 0:
        db.open("WTE_player")
        db.data[item["WTE_ITEM_INFO"]["user_id"]]["location"] = location
        log("玩家位置已变更.","WTE")
        db.save()
    log(f"{name} 已添加到 {location}","WTE")

def player_register(msg, sc):
    if "private" in msg["cid"]:
        db = database("WTE_player")
        db.open()
        db.save()
        player_data = db.read()
        if msg["user"]["id"] not in player_data:
            player = {
                "WTE_ITEM_INFO": { #特殊key
                    "type": 0,
                    "name": "",
                    "description": "一位蓝色星球上的旅人。",
                    "user_id": msg["user"]["id"],
                },
                "背包": {
                    "WTE_ITEM_INFO": {
                        "type": 1, # backpack
                        "description": "一个精致的皮革背包。",
                        "name": "背包",
                    },
                },
            }
            player_info = {
                "location": [],
                "wake": False,
                "last_act_time": time.time(),
                "name": "",
                "contained": "",
                "looked": "",
            }
            while True:
                player_name = get(msg["cid"], msg["user"]["id"], "[WTE] 旅人，你叫什么名字？",timeout_rsp=False)
                if player_name != None:
                    if "-" in player_name or " " in player_name:
                        ssend(msg["cid"], "[WTE] 名字内包含程序关键字符。")
                        continue
                    confrim = get(msg["cid"], msg["user"]["id"], "[WTE] "+ player_name + "，你确定吗？(y/n)",timeout_rsp=False)
                    if  confrim == "y" or confrim == "Y":
                        player["WTE_ITEM_INFO"]["user_id"] = msg["user"]["id"]
                        player["WTE_ITEM_INFO"]["name"] = player_name
                        player["背包"]["WTE_ITEM_INFO"]["description"] = f"一个精致的皮革背包。上面写着「{player_name}」。"
                        player_info["name"] = player_name
                        player_info["last_act_time"] = time.time()
                        db.open()
                        db.data[msg["user"]["id"]] = player_info
                        db.save()
                        item_append(player_name, player, ["测试聊天室"])
                        break
                    elif confrim == "n" or confrim == "N":
                        continue
                    else:
                        ssend(msg["cid"], "[WTE] 注册失败。")
                        break
                else:
                    ssend(msg["cid"], "[WTE] 注册失败。")
                    break
        else:
            ssend(msg["cid"], f"[WTE] 你已经注册过了,{player_data[msg['user']['id']]['name']}。")

def WORLDPAYLOAD(msg, sc):
    world = {
        "WTE_ITEM_INFO": {
            "type": -1,
            "name": "WTE",
            "description": "「世界」",
        },
        "测试聊天室": {
            "WTE_ITEM_INFO": {
                "type": -1,
                "name": "测试聊天室",
                "description": "BETA版本-测试聊天室",
            },
            "沙发": {
                "WTE_ITEM_INFO": {
                    "type": 2, # seat
                    "contain": "沙发上的",
                    "contain_info": "你坐在沙发上。",
                    "description": "一个非常大的沙发。",
                    "name": "沙发",
                },
            },
            "收音机": {
                "WTE_ITEM_INFO": {
                    "type": 3, # object
                    "description": "一个可以放歌(经典的网易云解析)的收音机。",
                    "name": "收音机",
                    "acts": {
                        "调频": "wte_ncm_radio",
                    },
                },
            },
        },
    }
    db = database("WTE_world")
    db.open()
    db.data = world
    db.save()

def player_act_time_update(user_id):
    db = database("WTE_player")
    db.open()
    if user_id in db.data:
        db.data[user_id]["last_act_time"] = time.time()
        db.data[user_id]["wake"] = True
    db.save()
    del db
    return

def player_wake_status_update():
    db = database("WTE_player")
    db.open()
    for user_id in db.data:
        if (time.time() - db.data[user_id]["last_act_time"]) >= 300:
            db.data[user_id]["wake"] = False
    db.save()
    del db
    log("Player wake status updated. Now wait 60s.","WTE")
    time.sleep(60)
    return

def move(item_name: str, from_location, to_location):
    pattern = r"-+\d+$"
    item_name = re.sub(pattern, "", item_name)
    db = database("WTE_world")
    db.open()
    place = db.data
    for key in from_location:
        place = place[key]
    if item_name in place:
        item = place.pop(item_name)
        log(item)
        if item["WTE_ITEM_INFO"]["type"] >= 0:
            place = db.data
            for key in to_location:
                place = place[key]
            if item_name not in place:
                place[item_name] = item
                db.save()
            else:
                n = 1
                while True:
                    if (item_name + str(n)) not in place:
                        name = item_name + "-" + str(n)
                        place[name] = item
                        db.save()
                        break
                    n += 1
            log(f"Moved Item [{item_name}] from {from_location} to {to_location}.")
            if item["WTE_ITEM_INFO"]["type"] == 0:
                db.open("WTE_player")
                db.data[item["WTE_ITEM_INFO"]["user_id"]]["location"] = to_location
                log("玩家位置已变更.","WTE")
                db.save()
            return item
        else:
            log(f"Moving Item type {str(item['WTE_ITEM_INFO']['type'])}.","WTE")
            db.save()
            return item
        db.save()


def check(msg, sc):
    if "private" in msg["cid"]:
        player_act_time_update(msg["user"]["id"])
        db = database("WTE_player")
        db_world = database("WTE_world")
        player_data = db.read()
        world_data = db_world.read()
        place = world_data
        player_location = player_data[msg["user"]["id"]]["location"]
        db.open()
        player_data = deepcopy(db.data)
        db.data[msg["user"]["id"]]["contained"] = ""
        db.save()
        for key in player_location:
            place = place[key]
        if not sc: #检查环境
            sight = "你环顾四周。\n" + place["WTE_ITEM_INFO"]["description"]
            for key in place:
                if key != "WTE_ITEM_INFO":
                    sight += "\n" + key + ": " + place[key]["WTE_ITEM_INFO"]["description"]
            ssend(msg["cid"], sight)
        else: #检查环境中的物品
            item = place
            for key in sc:
                try:
                    item = item[key]
                except:
                    ssend(msg["cid"], "[WTE] 你在寻找一件不存在的事物。")
                    return
            item_display_name = ""
            sleep = ""
            if item["WTE_ITEM_INFO"]["type"] != 0: #不是用户
                if "contained" in item["WTE_ITEM_INFO"]:
                    if item["WTE_ITEM_INFO"]["contained"] != "":
                        item_display_name += f"{item['WTE_ITEM_INFO']['contained']}"
                if "looked" in item["WTE_ITEM_INFO"]:
                    if item["WTE_ITEM_INFO"]["looked"] != "":
                        item_display_name += f"{item['WTE_ITEM_INFO']['looked']}"
            else: #是用户 这是为了方便随时更改玩家的状态，因为获取到玩家本身的位置会变得麻烦
                if "wake" in player_data[msg["user"]["id"]]:
                    if player_data[msg["user"]["id"]]["wake"] == False:
                        sleep = "(睡着了)"
                    else:
                        sleep = ""
                if "contained" in player_data[msg["user"]["id"]]:
                    if player_data[msg["user"]["id"]]["contained"] != "":
                        item_display_name += f"{player_data[msg['user']['id']]['contained']}"
                if "looked" in player_data[msg["user"]["id"]]:
                    if player_data[msg["user"]["id"]]["looked"] != "":
                        item_display_name += f"{player_data[msg['user']['id']]['looked']}"
            item_display_name += f"「{item['WTE_ITEM_INFO']['name']}」{sleep}"
            sight = f"你仔细看了看{item_display_name}。"
            if "description" in item["WTE_ITEM_INFO"]:
                sight += "\n" + item["WTE_ITEM_INFO"]["description"]
            for key in item:
                if key != "WTE_ITEM_INFO":
                    sight += "\n" + key + ": " + item[key]["WTE_ITEM_INFO"]["description"]
            ssend(msg["cid"], sight)

def say(msg, sc):
    if "private" in msg["cid"]:
        player_act_time_update(msg["user"]["id"])
        if sc:
            player_say = ' '.join(str(e) for e in sc)
            db = database("WTE_player")
            db_world = database("WTE_world")
            player_data = db.read()
            world_data = db_world.read()
            place = world_data
            player_location = player_data[msg["user"]["id"]]["location"]
            player_name = player_data[msg["user"]["id"]]["name"]
            for key in player_location:
                place = place[key]
            player_send_list = []
            for key in place:
                if key != "WTE_ITEM_INFO":
                    if place[key]["WTE_ITEM_INFO"]["type"] == 0:
                        if player_data[place[key]["WTE_ITEM_INFO"]["user_id"]]["wake"]:
                            player_send_list.append(place[key]["WTE_ITEM_INFO"]["user_id"])
            for player_send in player_send_list:
                ssend("private:" + player_send, f"{player_name}：{player_say}")
            log(f"[WTE] {player_name}对 {' '.join(str(e) for e in player_send_list)} 说 {player_say}。")

def use(msg, sc):
    if "private" in msg["cid"]:
        player_act_time_update(msg["user"]["id"])
        if sc:
            db = database("WTE_player")
            db_world = database("WTE_world")
            player_data = db.read()
            world_data = db_world.read()
            place = world_data
            player_location = player_data[msg["user"]["id"]]["location"]
            player_name = player_data[msg["user"]["id"]]["name"]
            for key in player_location:
                place = place[key]
            player_send_list = []
            for key in place:
                if key != "WTE_ITEM_INFO":
                    if place[key]["WTE_ITEM_INFO"]["type"] == 0:
                        player_send_list.append(place[key]["WTE_ITEM_INFO"]["user_id"])
            item = place
            for key in sc:
                try:
                    item = item[key]
                except:
                    ssend(msg["cid"], "[WTE] 你在寻找一件不存在的事物。")
                    return
            item_type = item["WTE_ITEM_INFO"]["type"]
            if item_type == 0: # player
                ssend(msg["cid"], f"[WTE] 你想使用「{item['WTE_ITEM_INFO']['name']}」xD")
            elif item_type == 1: # container
                pass
            elif item_type == 2: # seat
                db.open()
                db.data[msg["user"]["id"]]["contained"] = f"{item['WTE_ITEM_INFO']['contain']}"
                db.save()
                ssend(msg["cid"], f"[WTE] {item['WTE_ITEM_INFO']['contain_info']}")
            elif item_type == 3: # object
                ask = f"你想使用「{item['WTE_ITEM_INFO']['name']}」:(20s)\n"
                for act in item['WTE_ITEM_INFO']['acts']:
                    ask += f"[{act}] "
                rsp = get(msg["cid"], msg["user"]["id"], ask, timeout=20, timeout_rsp=False)
                if rsp is None:
                    ssend(msg["cid"], "你其实并不想用。")
                    return
                elif rsp not in item['WTE_ITEM_INFO']['acts']:
                    ssend(msg["cid"], "……看来你并不知道怎么用。")
                    return
                else:
                    func_name = item['WTE_ITEM_INFO']['acts'][rsp]
                    func = importlib.import_module(f"plugins.WTE_functions.{func_name}")
                    data = {
                        "player_send_list": player_send_list,
                        "player_data": player_data,
                        "world_data": world_data,
                    }
                    func.main(msg, data)
                    del func
            elif item_type == -2: # door
                from_location = player_data[msg["user"]["id"]]["location"]
                to_location = item["WTE_ITEM_INFO"]["target"]
                info = item["WTE_ITEM_INFO"]["targeted"]
                log(player_name)
                log(from_location)
                log(to_location)
                move(player_name, from_location, to_location)
                ssend(msg["cid"], f"你进入了「{to_location[len(to_location)-1]}」。\n- {info}")


def loads():
    plugin_registry(name="WTE", description="WTE", usage="注册 /register\n查看周围 /check\n查看某物品 /check [物品名]\n使用某物品 /use [物品名]\n向范围内玩家说话 /say [内容]", status=True)
    load_trigger(name="WTE", type="cmd", func=WORLDPAYLOAD, trigger="WORLDPAYLOAD", block=True, permission="superusers")
    load_trigger(name="WTE", type="cmd", func=player_register, trigger="register", block=True, permission="all")
    load_trigger(name="WTE", type="cmd", func=check, trigger="check", block=True, permission="all")
    load_trigger(name="WTE", type="cmd", func=say, trigger="say", block=True, permission="all")
    load_trigger(name="WTE", type="cmd", func=use, trigger="use", block=True, permission="all")
    load_trigger(name="WTE", type="services", func=player_wake_status_update, trigger="WTEPlayerWakeStatusUpdater")
