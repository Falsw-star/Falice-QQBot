from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from sender import ssend
from time import sleep
import datetime
import requests, json
def calendar(day,msg):
    headers = {
        "User-Agent": "falsw-star/falice-qq-bot"
    }
    try:
        rsp = json.loads(requests.get("https://api.bgm.tv/calendar", headers=headers, timeout=10).text)
    except Exception as e:
        ssend(msg["cid"],f"获取失败:{e}")
        return
    reply = ""
    if day == "all":
        rsp = rsp[0:7]
    else:
        rsp = [rsp[day]]
    for i in rsp:
        weekday = i["weekday"]
        num = 1
        reply = reply + "---" + weekday["en"] + "/" + weekday["cn"] + "/" + weekday["ja"] + "---" +"\n"
        for bangumi in i["items"]:
            reply = reply + str(num) + " "
            num += 1
            if bangumi["name_cn"] == "":
                reply = reply + bangumi["name"] + "\n"
            else:
                reply = reply + bangumi["name_cn"] + " (" + bangumi["name"] + ")\n"
    reply += "\n数据来源：https://api.bgm.tv/calendar"
    ssend(msg['cid'],reply)
    return

days = [1,2,3,4,5,6,7]
def bgm_handle(msg,sc):
    if sc:
        if(sc[0] == "all"):
            calendar("all",msg)
        else:
            try:
                sc[0] = int(sc[0])
                if(sc[0] in days):
                    calendar(sc[0]-1,msg)
                else:
                    ssend(msg['cid'],"请输入正确的数字")
                    return
            except:
                ssend(msg['cid'],"请输入正确的数字")
                return
    else:
        calendar(datetime.datetime.now().weekday(), msg)
def loads():
    plugin_registry(name="bangumi_calendar", usage="/bgm",status=True)
    load_trigger(name="bangumi_calendar", type="cmd", func=bgm_handle, trigger="bgm", permission="all")