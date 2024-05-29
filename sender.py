from adapters.adapter_satori import message_create as message_create
from adapters.adapter_satori import message_get as message_get
from adapters.adapter_satori import message_delete as message_delete
from adapters.adapter_satori import guild_list as guild_list
from adapters.adapter_satori import guild_member_get as guild_member_get
from adapters.adapter_satori import guild_member_list as guild_member_list
import time

from logger import log

#预定消息发送列表
SCHEDULEDSEND = []

#获取用户回复列表和回复列表
GOTLIST = []
GOT_RSP = []

#发送预定消息
def ssend(channel_id: str, content: str):
    global SCHEDULEDSEND
    SCHEDULEDSEND.append([channel_id, content])

#获取用户回复
def get(channel_id: str, user_id: str, ask_content: str, timeout: int = 20):
    global GOTLIST
    GOTLIST.append([channel_id, user_id])
    log(ask_content, "INFO")
    message_create(channel_id, f"<at id='{user_id}'/> {ask_content}")
    for i in range(0, timeout):
        if GOT_RSP:
            for rsp in GOT_RSP:
                if rsp[0] == channel_id and rsp[1] == user_id:
                    rsp_content = rsp[2]
                    GOT_RSP.remove(rsp)
                    return rsp_content
        time.sleep(1)
    #超时,取消任务
    GOTLIST.remove([channel_id, user_id])
    message_create(channel_id, f"等待{user_id}回复超时({timeout}s)")
    return None

def send_message(channel_id: str, content: str):
    message_create(channel_id, content)

def get_user(guild_id: str, user_id: str):
    return guild_member_get(guild_id, user_id)