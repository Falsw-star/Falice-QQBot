from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from mcstatus import JavaServer
from logger import log
import os
import time
from mcstatus import BedrockServer

def progress(msg, level):#多线程中进度保存
    path = "progress/mc"
    file_path = "progress/mc/" + msg["guild"]["name"] + msg["guild"]["id"] + ".txt"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file_path, "a+") as f:
        f.seek(0)  # 将文件指针移回文件开头
        lines = f.readlines()
        found = False
        for line_number, line in enumerate(lines):
            if msg["user"]["id"] in line:
                lines[line_number] = msg["user"]["id"] + ":" + level + "\n"#空格会崩，原因未知
                found = True
                break
        if not found:
            lines.append(msg["user"]["id"] + ":" + level + "\n")
        with open(file_path, "w+") as fe:
            fe.writelines(lines)

def save(msg,IP,NAME):
    path = "save"
    file_path = "save/mc.txt"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file_path, "a+") as f:
        f.seek(0)  # 将文件指针移回文件开头
        lines = f.readlines()
        found = False
        for line_number, line in enumerate(lines):
            if IP in line:
                lines[line_number] =  NAME+":"+IP+"\n"
                found = True
                break
        if not found:
            lines.append(NAME+":"+IP+"\n")
        with open(file_path, "w+") as fe:
            fe.writelines(lines)    
            
def mc(msg,special_content):
    if msg["content"] == "我的世界" :
        progress(msg,"1")
        message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n[开启服务器]\n[关闭服务器]\n查询惊变[惊变]\n服务器列表[列表]\n删除服务器[删除+名字]\n查询服务器[查询+地址]")

def 查询服务器(msg,special_content):#查询，添加，惊变
    file_path = "progress/mc/" + msg["guild"]["name"] + msg["guild"]["id"] + ".txt"
    with open(file_path, "r") as f:
        if  msg["user"]["id"] + ":1" in f.read():
            progress(msg,"0")
            if  msg["content"] == "惊变" :
                IP = "frp-fee.top:27502"
            else:
                IP=msg["content"][2:].lstrip()
            try:
                server = JavaServer.lookup(IP)
                server.ping
                status = server.status()        
                latency = server.ping()
                speak = f"Java版\n名称:{status.motd.parsed[0]}\nIP:{IP}\n延时:{int(latency)}ms\n版本:{status.version.name}\n在线人数:{status.players.online}\n"
                save(msg,IP,status.motd.parsed[0])
            except:
                speak = "未成功连接Java版\n"
            if  "查询" in  msg["content"] :
                try:   
                    server = BedrockServer.lookup(IP)
                    status = server.status()
                    speak  += f"\n基岩版\n名称:{status.motd.parsed[0]}\n当前人数:{status.players.online}\n延时:{int(status.latency)}ms"
                    save(msg,IP,status.motd.parsed[0])
                except:
                    speak  += "\n未成功连接基岩版"
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n{speak}")
def 服务器列表(msg,special_content):    
    file_path = "progress/mc/" + msg["guild"]["name"] + msg["guild"]["id"] + ".txt"
    with open(file_path, "r") as f:
        if  msg["user"]["id"] + ":1" in f.read():
            progress(msg,"0") 
            if  "列表"  in  msg['content']:   
                with open("save/mc.txt", "r") as fe:
                    line  = ''.join(fe.readlines())
                    line  = line.lstrip()
                    if line :
                        message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>喵\n{line}")
                    else:
                        message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>喵~没有哦")

def 删除(msg,special_content):
    file_path = "progress/mc/" + msg["guild"]["name"] + msg["guild"]["id"] + ".txt"
    with open(file_path, "r") as f:
        if  msg["user"]["id"] + ":1" in f.read():
           progress(msg,"0") 
        new = ''
        fOund = False
        de= msg['content'][2:].lstrip()
        with open ("save/mc.txt", "r") as fe :
            F =fe.readlines()    
            for line in F:
                if line[:line.find(":")] !=  de:
                    new +=line
                    new += '\n'
                else :
                    fOund=True
        with open ("save/mc.txt", "w") as fe :
            fe.writelines(new);  
        if  fOund   :
            message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>删除成功")
        else:
            message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>该服务器不存在")
     
def loads():
    plugin_registry(name="我的世界", usage="我的世界",status=True)
    load_trigger(name="我的世界", type="start", func=mc, trigger="我的世界", permission="all")
    plugin_registry(name="查询服务器", usage="查询+服务器地址,有添加功能",status=True)
    load_trigger(name="查询服务器", type="start", func=查询服务器, trigger="查询", permission="all",block=True)
    plugin_registry(name="查询惊变", usage="惊变",status=True)
    load_trigger(name="查询惊变", type="start", func=查询服务器, trigger="惊变", permission="all")
    plugin_registry(name="服务器列表", usage="列表",status=True)
    load_trigger(name="服务器列表", type="start", func=服务器列表, trigger="列表", permission="all")
    plugin_registry(name="删除服务器", usage="删除+",status=True)
    load_trigger(name="删除服务器", type="start", func=删除, trigger="删除", permission="all")