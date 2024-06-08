import websocket, httpx
import json
try:
    import thread # type: ignore
except ImportError:
    import _thread as thread
import time
from logger import log

#变量
STATUS = False #总开关
MASSAGE_LIST = [] #消息列表
LOGIN = { #账号信息
    "platform": "",
    "id": "",
    "status": None
}
HEARTBEATS = 0

from CONFIG import PLATFORMTOKEN
def on_open(ws):

    #鉴权连接
    if PLATFORMTOKEN:
        token = PLATFORMTOKEN
    else:
        token = "1ab98aa24bc602323851dbf82fd273af1907c0e39c06c1e04e1907aff4320c05" # 这个是Falsw开发时的token哦
    IDENTIFY = {
        "op": 3,
        "body": {
            "token": token,
        } 
    }
    IDENTIFY = json.dumps(IDENTIFY, ensure_ascii=False)
    ws.send(IDENTIFY)




def on_message(ws, message):
    try:
        op = json.loads(message)["op"]
        if op == 4: #logins
            global LOGIN
            body = json.loads(message)["body"]
            LOGIN["platform"] = body["logins"][0]["platform"]
            LOGIN["id"] = body["logins"][0]["user"]["id"]
            LOGIN["status"] = body["logins"][0]["status"]
            log("WebSocket连接到账号: " + LOGIN["platform"] + " - " + LOGIN["id"],"SUCCESS")
            #总开关，启动
            global STATUS
            STATUS = True
            #Satori协议要求的PING
            def ping():
                PING = json.dumps(
                    {
                        "op": 1
                    }
                )
                global STATUS
                while True:
                    time.sleep(10)
                    if STATUS == True:
                        ws.send(PING)
                    else:
                        break
            thread.start_new_thread(ping,())
        elif op == 2: # pongs
            global HEARTBEATS
            HEARTBEATS += 1
        elif op == 0: #events
            global MASSAGE_LIST
            body = json.loads(message)["body"]
            if body["channel"]["type"] == 0:
                msg = {
                    "type": 0, #消息类型 int (私聊)
                    "timestamp": body["timestamp"], #时间戳 int
                    "user": { #消息发送者 dict
                        "id": body["user"]["id"], #发送者id(QQ号) str(int)
                        "name": "", #发送者昵称 str
                        "avatar": body["user"]["avatar"] #发送者头像 str(url)
                    },
                    "guild": body["guild"], #消息所在群 dict{"id":群号 str(int), "name":群名 str, "avatar":群头 str(url)}
                    "id": body["message"]["id"], #本条消息id str(int)
                    "content": body["message"]["content"], #消息内容 str
                    "cid": body["channel"]["id"] #频道id(要回复的对象) str
                }
                if body["member"]:
                    msg["user"]["name"] = body["member"]["nick"]
            elif body["channel"]["type"] == 1:
                msg = {
                    "type": 1, #消息类型 int (私聊)
                    "timestamp": body["timestamp"], #时间戳 int
                    "user": { #消息发送者 dict
                        "id": body["user"]["id"], #发送者id(QQ号) str(int)
                        "name": "", #发送者昵称 str
                        "avatar": body["user"]["avatar"] #发送者头像 str(url)
                    },
                    "guild": {},
                    "id": body["message"]["id"], #本条消息id str(int)
                    "content": body["message"]["content"], #消息内容 str
                    "cid": body["channel"]["id"] #频道id(要回复的对象) str
                }
            if msg["type"] == 0:
                channel = msg["guild"]["name"] + f"({msg['guild']['id']})"
            elif msg["type"] == 1:
                channel = msg["cid"]
            log(str(channel) + "-" + msg["user"]["name"] + f"({msg['user']['id']}) : " + msg["content"], "CHAT")
            MASSAGE_LIST.append(msg)
    except Exception as e:
        log(f"消息解析失败: {str(e)}", "WARNING")

def on_error(ws, error):
    #总开关，关闭
    global STATUS
    STATUS = False
    log(f"WebSocket连接失败: {str(error)}", "WARNING")
    

def on_close(ws):
    #总开关，关闭
    global STATUS
    STATUS = False
    log("WebSocket连接关闭", "WARNING")

from CONFIG import WSBASE
def run():
    if WSBASE:
        url = WSBASE
    else:
        url = "ws://localhost:5500/v1/events"
    ws = websocket.WebSocketApp(
        url=url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.url = url
    ws.on_open = on_open
    while True:
        try:
            log("尝试连接WebSocket...","RUNTIME")
            ws.run_forever()
            time.sleep(3)
        except Exception as e:
            log(f"WebSocket连接失败: {str(e)}", "WARNING")

#calling_api部分
from CONFIG import HTTPBASE
if HTTPBASE:
    base = HTTPBASE
else:
    base = "http://localhost:5500/v1/"
data = {}
def request(url, data = data):
    if PLATFORMTOKEN:
        token = PLATFORMTOKEN
    else:
        token = "1ab98aa24bc602323851dbf82fd273af1907c0e39c06c1e04e1907aff4320c05" # 是Falsw开发时的token呢
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
        "X-Platform": LOGIN["platform"],
        "X-Self-ID": LOGIN["id"]
    }
    rsp = httpx.post(base + url, headers=headers, json=data, timeout=10).text
    return rsp

def guild_list(next = None):
    log("CallingAPI: guild.list", "DEBUG")
    data = {
        "next": next
    }
    return request("guild.list", data=data)

def message_create(channel_id: str, content: str):
    log("CallingAPI: message_create", "DEBUG")
    data = {
        "channel_id" : channel_id,
        "content": content
    }
    return request("message.create", data=data)

def message_get(channel_id: str, message_id: str):
    log("CallingAPI: message_get", "DEBUG")
    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }
    return request("message.get", data=data)

def message_delete(channel_id: str, message_id: str):
    log("CallingAPI: message_delete", "DEBUG")
    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }
    return request("message.delete", data=data)

def guild_member_get(guild_id: str, user_id: str):
    log("CallingAPI: guild_member_get", "DEBUG")
    data = {
        "guild_id": guild_id,
        "user_id": user_id
    }
    return request("guild.member.get", data=data)

def guild_member_list(guild_id: str, next: str = "0"):
    log("CallingAPI: guild_member_list", "DEBUG")
    data = {
        "guild_id": guild_id,
        "next": next
    }
    return request("guild.member.list", data=data)

def friend_list(next: str = "0"):
    log("CallingAPI: friend_list", "DEBUG")
    data = {
        "next": next
    }
    return request("friend.list", data=data)