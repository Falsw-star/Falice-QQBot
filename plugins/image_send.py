from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
import os#创建文件夹
from logger import log
import random
from logger import cfp

def 捞图(msg,special_content):
    if msg["content"] == "图":
        folder_path = cfp + "/image/" + msg["guild"]["name"] + '-' + msg['cid']
        image_files = get_image_files(folder_path)
        random_image = select_random_image(image_files)
        message_create(msg['cid'],f"<at id='{msg['user']['id']}'/><img src='file:///{folder_path}/{random_image}'/>")
    
def get_image_files(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']# 其实只有jpg
    image_files = []
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    return image_files

def select_random_image(image_files):
    return random.choice(image_files)

def loads():
    plugin_registry(name="捞图", usage="图",status=True)
    load_trigger(name="捞图", type="start", func = 捞图, trigger="图", permission="all")