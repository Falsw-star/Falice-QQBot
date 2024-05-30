from matcher import load_trigger, plugin_registry
from adapters.adapter_satori import message_create
from mcstatus import JavaServer
from logger import log
import os
from mcstatus import BedrockServer
from op import opt
from op import MC,USER,CONTENT
import subprocess
            
def mc(msg,special_content):
    if msg["content"] == "我的世界" :
        message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n查询惊变[惊变]\n开启服务器[启动]\n关闭服务器[关闭]\n服务器列表[列表]\n查询并添加[查询+地址]\n删除服务器[删除+名字]]")

def 查询并添加(msg,special_content):#查询，添加，惊变
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
        opt(msg,"mc",IP+"-"+str(status.motd.parsed[0]),"1",False)
    except:
        speak = "Java版\n未成功连接\n"
    if  "查询" in  msg["content"] :
        try:   
            server = BedrockServer.lookup(IP)
            status = server.status()
            speak  += f"\n基岩版\n名称:{status.motd.parsed[0]}\n当前人数:{status.players.online}\n延时:{int(status.latency)}ms"
            opt(msg,"mc",IP+"-"+str(status.motd.parsed[0]),"1",False)
        except:
            speak  += "基岩版\n未成功连接"
    message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n{speak}")
def list(msg,special_content):    
    opt(msg,"mc")
def de(msg,special_content):
    opt(msg,"mc",msg['content'][2:].lstrip(),"2")

USER = ""
MC['100days']="0"
L = True# 是否输出到控制台
def is_mc_running(msg,special_content):
    global MC,USER,CONTENT
    if  msg["content"] == "启动" :
        if MC['100days']=="0":#0允许开启
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n正在启动喵")
            MC['100days']="1"#判断且拦截继续开启
            run(msg)
        else :
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n已经启动了喵")   
 
def is_mc_stop(msg,special_content):
    global MC,USER,CONTENT
    if msg["content"] == "关闭" :
        if MC['100days']=="3":
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n正在关闭喵")
            MC['100days']="4"
        else:
            message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n未开启喵")

def run(msg):
    global MC,USER,CONTENT
    new_directory = "F:/MISAKA_MIKOTO/YB17202H/我的世界/server/惊变"#切换工作目录
    os.chdir(new_directory)
    bat_file_path = r"F:/MISAKA_MIKOTO/YB17202H/我的世界/server/惊变/run.bat"
    try:
        process = subprocess.Popen(bat_file_path, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while True:
            output = process.stdout.readline()  # type: ignore
            if b'>pause' in output :
                message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n启动失败")
                log("启动失败","Minecraft")
                MC['100days'] = "0"
                break
            if output:
                if L :
                    log(output.strip().decode('gbk'),"Minecraft")
                if "Starting minecraft server version 1.18.2" in output.strip().decode('gbk'):
                    message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>\n启动成功")
                    MC['100days']="3"
                if MC['100days']=="4":
                    process.communicate(input=b'stop')
                    MC['100days']="0"
                if "按任意键" in output.strip().decode('gbk'):
                    message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>\n服务器已关闭")
##                if MC['100days']=="5":

##                    MC['100days']="3"
    except:
        message_create(msg["guild"]["id"],f"<at id='{msg['user']['id']}'/>喵\n启动失败")
        MC['100days']="0"

##def qq_server(msg,special_content):
##    global MC,USER,CONTENT
##    if  msg["guild"]['id'] == '636150815' and MC['100days']=="3":
##        USER =  msg["user"]['id']





def loads():
    plugin_registry(name="我的世界", usage="我的世界",status=True)
    load_trigger(name="我的世界", type="start", func=mc, trigger="我的世界", permission="all")

    plugin_registry(name="查询服务器", usage="查询+服务器地址,有添加功能",status=True)
    load_trigger(name="查询服务器", type="start", func=查询并添加, trigger="查询", permission="all",block=True)

    plugin_registry(name="查询惊变", usage="惊变",status=True)
    load_trigger(name="查询惊变", type="start", func=查询并添加, trigger="惊变", permission="all")

    plugin_registry(name="list", usage="list",status=True)
    load_trigger(name="list", type="start", func=list, trigger="列表", permission="all")

    plugin_registry(name="de", usage="删除+",status=True)
    load_trigger(name="de", type="start", func=de, trigger="删除", permission="all")

    plugin_registry(name="is_mc_running", usage="启动",status=True)
    load_trigger(name="is_mc_running", type="start", func=is_mc_running, trigger="启动", permission="all")

    plugin_registry(name="is_mc_stop", usage="关闭",status=True)
    load_trigger(name="is_mc_running", type="start", func=is_mc_stop, trigger="关闭", permission="all")

##    plugin_registry(name="qq_server", usage="将qq消息传入我的世界",status=True)
##   load_trigger(name="qq_server", type="all", func=qq_server, permission="all")