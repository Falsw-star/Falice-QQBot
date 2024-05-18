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
HEARTBEATS = []

def on_open(ws):

    #鉴权连接
    token = "1ab98aa24bc602323851dbf82fd273af1907c0e39c06c1e04e1907aff4320c05"
    IDENTIFY = {
        "op": 3,
        "body": {
            "token": token,
        } 
    }
    IDENTIFY = json.dumps(IDENTIFY, ensure_ascii=False)
    ws.send(IDENTIFY)

    #Satori协议要求的PING
    def ping():
        PING = json.dumps(
            {
                "op": 1
            }
        )
        while True:
            time.sleep(10)
            ws.send(PING)
    thread.start_new_thread(ping,())


def on_message(ws, message):
    try:
        op = json.loads(message)["op"]
        body = json.loads(message)["body"]
        if op == 4: #logins
            global LOGIN
            LOGIN["platform"] = body["logins"][0]["platform"]
            LOGIN["id"] = body["logins"][0]["user"]["id"]
            LOGIN["status"] = body["logins"][0]["status"]
            log("WebSocket连接到账号: " + LOGIN["platform"] + " - " + LOGIN["id"],"SUCCESS")
            #总开关，启动
            global STATUS
            STATUS = True
        elif op == 0: #events
            global MASSAGE_LIST
            msg = {
                "type": body["type"], #消息类型 str
                "timestamp": body["timestamp"], #时间戳 int
                "user": { #消息发送者 dict
                    "id": body["user"]["id"], #发送者id(QQ号) str(int)
                    "name": "", #发送者昵称 str
                    "avatar": body["user"]["avatar"] #发送者头像 str(url)
                },
                "guild": body["guild"], #消息所在群 dict{"id":群号 str(int), "name":群名 str, "avatar":群头 str(url)}
                "id": body["message"]["id"], #本条消息id str(int)
                "content": body["message"]["content"] #消息内容 str
            }
            if body["member"]:
                msg["user"]["name"] = body["member"]["nick"]
            log(msg["guild"]["name"] + "-" + msg["user"]["name"] + f"({msg['user']['id']}) : " + msg["content"], "CHAT")
            MASSAGE_LIST.append(msg)
    except Exception as e:
        pass

def on_error(ws, error):
    print(error)

def on_close(ws):
    #总开关，关闭
    global STATUS
    STATUS = False

def run():
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
    ws.run_forever()

#calling_api部分
base = "http://localhost:5500/v1/"

data = {}
def request(url, data = data):
    token = "1ab98aa24bc602323851dbf82fd273af1907c0e39c06c1e04e1907aff4320c05"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
        "X-Platform": LOGIN["platform"],
        "X-Self-ID": LOGIN["id"]
    }
    rsp = httpx.post(url, headers=headers, json=data, timeout=10).text
    return rsp

def guild_list():
    log("CallingAPI: guild.list","DEBUG")
    data = {
        "next": None
    }
    return request(base + "guild.list", data=data)

def message_create(channel_id: str, content: str):
    log("CallingAPI: message_create","DEBUG")
    data = {
        "channel_id" : channel_id,
        "content": content
    }
    return request(base + "message.create", data=data)