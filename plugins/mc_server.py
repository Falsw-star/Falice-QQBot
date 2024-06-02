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
        save(f"JAVA版-{status.motd.parsed[0]}",IP)
    except:
        speak = "Java版\n未成功连接\n"
    if  "/查询" in  msg["content"] :
        try:   
            server = BedrockServer.lookup(IP)
            status = server.status()
            speak  += f"\n基岩版\n名称:{status.motd.parsed[0]}\n延时:{int(status.latency)}ms\n当前人数:{status.players.online}\n"
            save(f"基岩版-{status.motd.parsed[0]}",IP)
        except:
            speak  += "基岩版\n未成功连接\n"
    speak += f"IP:{IP}\n"
    ssend(msg['cid'],speak)
def save(NAME,IP):
    db = database("mc_server")
    db.open()
    db.data[NAME]=IP
    db.save()
def list(msg,sc):
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

def delete(msg,sc):
    if len(sc)!=1:
        ssend(msg['cid'],"参数错误")
        return
    if exists("mc_server"):
        db = database("mc_server")
        db.open()
        if sc[0] in db.data:
            del db.data[sc[0]]
            db.save()
            ssend(msg['cid'],"删除成功")
            return
        ssend(msg['cid'],"删除失败")
    else:
        ssend(msg['cid'],"暂无服务器")
L = True# 是否输出到控制台
def is_mc_running(msg,sc):
    global MC,MCSD
    if MC['100days']=="0":#0允许开启
        message_create(msg['cid'],"正在启动")
        MC['100days']="1"#判断且拦截继续开启
        run(msg)
    else:
        message_create(msg['cid'],"已启动")   
 
def is_mc_stop(msg,sc):
    global MC,MCSD
    if MC['100days']=="3":
        message_create(msg['cid'],"正在关闭")
        MC['100days']="4"
    else:
        message_create(msg['cid'],"未开启服务器")
def run(msg):
    global MC, MCSD
    new_directory = "F:/MISAKA_MIKOTO/YB17202H/我的世界/server/惊变"#切换工作目录
    os.chdir(new_directory)
    bat_file_path = r"F:/MISAKA_MIKOTO/YB17202H/我的世界/server/惊变/run.bat"
    def read_output(process):
        while True:
            try:
                output = process.stdout.readline()
                if not output:
                    break
                if b'>pause' in output:
                    message_create(msg['cid'], "启动失败")
                    log("启动失败或异常关闭", "Minecraft")
                    MC['100days'] = "0"
                    break
                if "Starting minecraft server version" in output.decode('gbk'):
                    message_create(msg['cid'], "启动成功")
                    MC['100days'] = "3"
                if MC['100days'] == "4":
                    log('stop', 'mcsd')
                    process.stdin.write(b'stop\n')
                    process.stdin.flush()
                    MC['100days'] = "0"
                    break
                if "按任意键" in output.decode('gbk'):
                    message_create(msg['cid'], "服务器已关闭")
                if L:
                    log(output.strip().decode('gbk'), "Minecraft")
            except Exception as e:
                log(f"读取输出时发生错误: {e}", "Minecraft")
                break
    process = subprocess.Popen(bat_file_path, bufsize=0, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    output_reader_thread = threading.Thread(target=read_output, args=(process,))
    output_reader_thread.start()
    while True:
        if MCSD:
            try:
                command = MCSD.popleft()
                log(command, "mcsd")
                process.stdin.write((command+"\n").encode())
                process.stdin.flush()
            except Exception as e:
                log(f"发送命令时发生错误: {e}", "mcsd")
        if not process.poll() is None:
            break  # 子进程已结束
    # 清理资源
    process.stdin.close()
    process.stdout.close()
    return

def creat_P(msg, special_content):#获取生成粒子状态
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
                xx=float(USER['X'])
                yy=float(USER['Y'])
                for char in USER['content']:
                    if char != '\\' :
                        thread.start_new_thread(creat_char_image,(char,USER,xx,yy))
                        if '\u4e00' <= char <= '\u9fff':
                            xx+=75
                        else:
                            xx+=50
                    else:
                        yy+=70
                        xx=float(USER['X'])
                time.sleep(0.5)
            ssend(msg['cid'],"生成成功")
        except:
            ssend(msg['cid'],"生成错误")
    else:
        ssend(msg['cid'],"服务器未启动")
    pass
def creat_char_image(char,USER,xx,yy):
    img = Image.new('RGB', (80, 80), (255, 255, 255))
    font = ImageFont.truetype("C:/Windows/fonts/STXINWEI.TTF", 45)
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