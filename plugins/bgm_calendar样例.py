from nonebot.exception import MatcherException
from nonebot.plugin import PluginMetadata
from time import sleep

__plugin_meta__ = PluginMetadata(
    name="追番日历",
    description="获取每天的番剧更新",
    usage="/bgm; /bgm [1/2/3/4/5/6/7]; /bgm all",
    config=None,
)
import datetime
import requests, json
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

bgm = on_command("bgm", aliases={"追番"})

async def calendar(day,bgm):
    headers = {
        "User-Agent": "falsw-star/falice-qq-bot"
    }
    try:
        rsp = json.loads(requests.get("https://api.bgm.tv/calendar", headers=headers, timeout=10).text)
    except Exception as e:
        await bgm.finish(f"获取失败:{e}")
    reply = ""
    hr = "###############"
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
        reply += hr + "\n"
        await bgm.send(reply)
        reply = ""
        sleep(0.5)
    await bgm.finish("数据来源：https://api.bgm.tv/calendar")

days = [1,2,3,4,5,6,7]

@bgm.handle()
async def bgm_handle(message: Message = CommandArg()):
    if(day := message.extract_plain_text()):
        if(day == "all"):
            await calendar("all", bgm)
        else:
            try:
                day = int(day)
                if(day in days):
                    await calendar(day-1, bgm)
                else:
                    await bgm.finish("请输入正确的数字")
            except MatcherException:
                raise
            except:
                await bgm.finish("请输入正确的数字")
    else:
        await calendar(datetime.datetime.now().weekday(), bgm)
