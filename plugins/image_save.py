from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
import os#创建文件夹
import requests#网址爬取
try:
    import thread #type: ignore
except ImportError:
    import _thread as thread
import re#正则表达式？
from logger import cfp

def extract_strings(text):#提取网址
    pattern = r'"(.*?)"'
    result = re.findall(pattern, text)
    return result

def image(msg,special_content):
    thread.start_new_thread(run,(msg,))

def run(msg): 
    path =cfp+"/image/" + msg["guild"]["name"] + '-' + msg['cid']
    if not os.path.exists(path):
        os.makedirs(path)#创建文件夹

    text = extract_strings(msg["content"])
    text = ''.join(text)
    text = text.replace("127.0.0.1","localhost")#转换后网址

    picture = requests.get(text)#图片获取
    if picture.status_code == 200:
        with open(path + '/'+text[32:]+".jpg", "wb") as file:
          file.write(picture.content)
          file.close()
def loads():
    plugin_registry(name="image_save", usage="自动收集群聊图片",status=True)
    load_trigger(name="image_save", type="start", func= image, trigger="<img src=", permission="all")