from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from mcstatus import JavaServer
from logger import log
import os
from mcstatus import BedrockServer
import subprocess
from sender import ssend,get
try:
    import thread as thread  # type: ignore
except ImportError:
    import _thread as thread
from PIL import Image, ImageDraw, ImageFont
import time
import threading
from collections import deque
from db import database, exists
from folder_path import MCPATH,MAINPATH
import json
MC = {"100days":"0"}
MCSD = deque()
def search(msg,sc):#查询添加，惊变
    if  msg["content"] == "/惊变" :
        IP = "frp-fee.top:27502"
    else:
        if len(sc)!=1:
            ssend(msg['cid'],"参数错误")
            return
        IP = sc[0]
    try:
        server = JavaServer.lookup(IP)
        server.ping
        status = server.status()        
        latency = server.ping()
        speak = f"Java版\n名称:{status.motd.parsed[0]}\n延时:{int(latency)}ms\n版本:{status.version.name}\n在线人数:{status.players.online}\n"
        save_servers(status.motd.parsed[0],IP)
    except:
        speak = "Java版\n未成功连接\n"
    if  "/查询" in  msg["content"] :
        try:   
            server = BedrockServer.lookup(IP)
            status = server.status()
            speak  += f"\n基岩版\n名称:{status.motd.parsed[0]}\n延时:{int(status.latency)}ms\n当前人数:{status.players.online}\n"
            save_servers(status.motd.parsed[0],IP)
        except:
            speak  += "基岩版\n未成功连接\n"
    speak += f"IP:{IP}\n"
    ssend(msg['cid'],speak)
def save_servers(NAME,IP):#用于存储
    db = database("mc_server")
    db.open()
    db.data[NAME]=IP
    db.save()
def list(msg,sc):#列出服务器列表
    if exists("mc_server"):
        db = database("mc_server")
        db.open()
        speak = "服务器列表:\n"
        for NAME in db.data:
            speak += f"{NAME}:{db.data[NAME]}\n"
        ssend(msg['cid'],speak)
        return
    else:
        ssend(msg['cid'],"暂无服务器")
def delete(msg,sc):#删除列表中的服务器
    if len(sc)!=1:
        ssend(msg['cid'],"参数错误")
        return
    if exists("mc_server"):
        db = database("mc_server")
        db.open()
        if sc[0] in db.data:
            db.data.remove(db.data[sc[0]])
            db.save()
            ssend(msg['cid'],"删除成功")
            return
        ssend(msg['cid'],"删除失败")
    else:
        ssend(msg['cid'],"暂无服务器")
L = True# 是否输出到控制台
def is_mc_running(msg,sc):#发出启动信息
    global MC,MCSD
    if MC['100days']=="0":#0允许开启
        message_create(msg['cid'],"正在启动")
        MC['100days']="1"#判断且拦截继续开启
        run(msg)
    else:
        message_create(msg['cid'],"已启动")    
def is_mc_stop(msg,sc):#发出停止信息
    global MC,MCSD
    if MC['100days']=="3":
        MC['100days']="4"
        message_create(msg['cid'],"正在关闭")
    else:
        message_create(msg['cid'],"未开启服务器")
def run(msg):#启动服务器
    global MC, MCSD
    os.chdir(MCPATH)#切换工作目录
    bat_file_path = f"{MCPATH}/run.bat"
    def write_in(process):
        while True:
            if MC['100days'] == "4":
                MCSD.append("stop")
                MC['100days'] = "0"
            if MCSD:
                try:
                    command = MCSD.popleft()
                    log(command, "mcsd")
                    process.stdin.write((command+"\n").encode())
                    process.stdin.flush()
                except Exception as e:
                    log(f"发送命令时发生错误: {e}", "mcsd")
            if not process.poll() is None:
                break  # 子进程已结束`
    process = subprocess.Popen(bat_file_path, bufsize=0, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    write_in = threading.Thread(target=write_in, args=(process,))
    write_in.start()
    while True:
        global MC, MCSD
        try:
            output = process.stdout.readline()
            if not output:
                break
            if b'>pause' in output:
                ssend(msg['cid'], "启动失败")
                log("启动失败或异常关闭", "Minecraft")
                break
            if b"Starting minecraft server version" in output:
                ssend(msg['cid'], "启动成功")
                MC['100days'] = "3"
            if L:
                log(output.strip().decode('gbk'), "Minecraft")
        except Exception as e:
            log(f"读取输出时发生错误: {e}", "Minecraft")
            break
    process.stdin.close()
    process.stdout.close()
    ssend(msg['cid'],"服务器已关闭")
    log('服务器已关闭', 'Minecraft')
    MC['100days'] = "0"
    return
def creat_P(msg, special_content):#截取生成粒子的文字
    USER = {"X":"","Y":"","Z":"","content":"","P":"","N":"","D":1}
    if len(special_content) < 6:
        ssend(msg["cid"],"参数错误")
        return
    elif len(special_content) > 7:
        ssend(msg["cid"],"参数错误")
        return
    elif len(special_content) == 7:
        try:
            n = int(special_content[6])
            if USER["D"] < 1:#生成次数
                ssend(msg["cid"],"D错误")
            else:
                USER["D"] = n
        except:
            ssend(msg["cid"],"D错误")
    global MC,MCSD
    if MC['100days'] == "3":#服务器处于开启状态
        USER['content'] = special_content[0]#文本内容
        try:
            for i in range (0,USER["D"]):
                USER["P"]=special_content[1]#粒子
                USER["X"]=special_content[2]#X坐标
                USER["Y"]=special_content[3]#Y坐标
                USER["Z"]=special_content[4]#Z坐标
                USER["N"]=special_content[5]#粒子数量
                xx=0
                yy=0
                for char in USER['content']:
                    if char != '\n' :
                        thread.start_new_thread(creat_char_image,(char,USER,xx,yy))
                        if '\u4e00' <= char <= '\u9fff':
                            xx+=7.2
                        else:
                            xx+=4
                    else:
                        yy-=7.2
                        xx=0
                time.sleep(0.5)
            ssend(msg['cid'],"生成成功")
        except:
            ssend(msg['cid'],"生成错误")
    else:
        ssend(msg['cid'],"服务器未启动")
    pass
def creat_char_image(char,USER,xx,yy):#生成每个文字的像素粒子坐标
    img = Image.new('RGB', (80, 80), (255, 255, 255))
    font = ImageFont.truetype("C:/Windows/fonts/SIMLI.TTF", 45)
    text_bbox = font.getbbox(char)
    text_position = (10, 10)
    draw = ImageDraw.Draw(img)
    draw.text(text_position, char, fill=(0, 0, 0), font=font)
    actual_bbox = (text_position[0], text_position[1],
    text_position[0] + text_bbox[2], text_position[1] + text_bbox[3])
    for x in range(actual_bbox[0], actual_bbox[2]):
        for y in range(actual_bbox[1], actual_bbox[3]):
            pixel_color = img.getpixel((x, y))
            if pixel_color == (0, 0, 0):
                X = str(float(x/5)+float(USER["X"])+xx)
                Y = str(float(y/-5)+float(USER["Y"])+yy)
                MCSD.appendleft(f"particle minecraft:{USER['P']} {X} {Y} {USER["Z"]} 0 0.002 0 0.00005 {USER["N"]} force @a")
def creat_badapple(msg,sc):
    creat_meta("qqbot",18,"这里是blue")
    write_find_function("","qqbot","badapple",f"badapple1")
    def is_pixel_black(pixel):
        r, g, b = pixel
        return r == g == b == 0
    if len(sc)==3:
        USER={"X":sc[0],"Y":sc[1],"Z":sc[2]}
        tick = 1
        while(tick < 6562):
            j = tick
            for i in range(0,90):
                write_find_function("","qqbot","badapple",f"badapple{str(i)}","world",True)
                writein = ""
                with Image.open(f"{MAINPATH}/badapple/{tick}.png") as img:
                    pixels = img.load()
                    width, height = img.size
                    for y in range(0,height,2):
                        for x in range(0,width,2):
                            if is_pixel_black(pixels[x, y]):
                                X = str(int(x/2)+int(USER["X"]))
                                Y = str(int(y/-2)+int(USER["Y"]))
                                #writein +=f"particle minecraft:squid_ink {X} {Y} {USER["Z"]} 0 0.002 0 0.00005 1 force @a\n"
                                writein +=f"setblock {X} {Y} {USER["Z"]} black_concrete\n"
                            else:
                                X = str(int(x/2)+int(USER["X"]))
                                Y = str(int(y/-2)+int(USER["Y"]))
                                writein+= f"setblock {X} {Y} {USER["Z"]} white_concrete\n"
                if i!=90:
                    writein+=f"schedule function badapple:badapple{str(i+1)} 1 append"
                write_find_function(writein,"qqbot","badapple",f"badapple{str(i)}")
                log(f"生成:{str(i+1)}\n     总量{str(tick-1)}")
                tick+=1
                ssend(msg['cid'],f"生成:{str(i+1)}\n总量{str(tick-1)}")
            MCSD.appendleft("reload")
            time.sleep(6)
            MCSD.appendleft(f"function badapple:badapple0")
            time.sleep(8)
        ssend(msg['cid'],"生成成功")
    else:
        ssend(msg['cid'],"参数错误")
def creat_meta(packet_name,version,description="",world="world"):#创建或更改同名数据包
    dic = {}
    if packet_name.islower():#数据包名称必须为小写字母组成的字符串 且不为空
        packet_path = f"{MCPATH}/{world}/datapacks/{packet_name}"
        if not os.path.exists(packet_path):
            os.makedirs(packet_path)#生成数据包文件夹
        if version == None or description == "":
            if os.path.exists(f"{packet_path}/pack.mcmeta"):
                with open(f"{packet_path}/pack.mcmeta", "r", encoding="utf-8") as f:
                    dic =json.load(f)
                    if "pack" in dic and "pack_format" in dic["pack"] and "description" in dic["pack"]:
                        if dic["pack"]["pack_format"] and dic["pack"]["description"]:
                            version = dic["pack"]["pack_format"]
                            description = dic["pack"]["description"]
                        else:
                            return "更改数据包失败"
                    else:
                            return "更改数据包失败"
            else:
                return "更改数据包失败"
        if version not in [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
            return "数据包版本错误 1.13-1.20.3"  
        with open(f"{packet_path}/pack.mcmeta", "w", encoding="utf-8") as f:#生成数据包文件
            dic = {
                "pack": {
                    "pack_format": version,
                    "description": description
                }
            }
            json.dump(dic,f,ensure_ascii=False,indent=4)
        return "1"
    return "数据包命名失败或不存在"
def write_find_function(content,packet_name,function_folder_name,function_name,world="world",clear=False,functions_folder_name=""):#写入函数，clear=false时查询函数，True时清空函数创建
    if packet_name.islower() and function_name.islower() and function_folder_name.islower():#为小写字母组成的字符串且不为空
        if functions_folder_name != "":#里面一层
            if functions_folder_name.islower():
                functions_folder_name = "/"+functions_folder_name
            else:
                return "无此函数"
        function_path = f"{MCPATH}/{world}/datapacks/{packet_name}/data/{function_folder_name}/functions{functions_folder_name}"
        if clear :
            with open(f"{function_path}/{function_name}.mcfunction", "w", encoding="utf-8") as f:
                f.write("")
                return "清空成功"
        if not os.path.exists(function_path):
            os.makedirs(function_path)
        with open(f"{function_path}/{function_name}.mcfunction","a", encoding="utf-8") as f:
            f.write(content+"\n")
        return f"function {function_folder_name}{functions_folder_name}:{function_name}"
    return "无此函数"
def test(msg,sc):
    ssend(msg['cid'],(sc[0],sc[1],sc[2]))
def loads():
    usage = "{/启动}开启服务器\n{/关闭}关闭服务器\n{/列表}服务器列表\n{/查询 服务器IP}查看服务器状态\n{/删除 服务器ID}删除服务器记录\n{/惊变}惊变服务器查询"
    plugin_registry(name="mc_server", usage=usage,status=True)
    load_trigger(name="mc_server", type="cmd", func=search, trigger="查询", permission="all")
    load_trigger(name="mc_server", type="cmd", func=search, trigger="惊变", permission="all")
    load_trigger(name="mc_server", type="cmd", func=list, trigger="列表", permission="all")
    load_trigger(name="mc_server", type="cmd", func=delete, trigger="删除", permission="all")
    load_trigger(name="mc_server", type="cmd", func=is_mc_running, trigger="启动", permission="all")
    load_trigger(name="mc_server", type="cmd", func=is_mc_stop, trigger="关闭", permission="all")
    load_trigger(name="mc_server", type="cmd", func=creat_P, trigger="生成", permission="all")
    load_trigger(name="mc_server", type="cmd", func=test, trigger="test", permission="all")
    load_trigger(name="mc_server", type="cmd", func=creat_badapple, trigger="creat_badapple", permission="all")