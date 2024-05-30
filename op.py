import os
from adapters.adapter_satori import message_create
from logger import cfp
MC = {"100days":"0"}
USER = ""
CONTENT =""
def opt(msg,name,content="",t="0",block=True):#msg 回复讯问人员 ma回复内容 content字符串，添加要存储的内容  name 字符串，存储名称 位置/save/name 有去重功能 c 1,添加，2，删除，3，列举
    path = cfp+"/save/"+name+".txt"
    content=content.strip()
    if  t == "1":        
        if not os.path.exists("save/"):
            os.makedirs("save/")
        with open(path, "a+") as f:
            f.seek(0)  # 将文件指针移回文件开头
            lines = f.readlines()
            found = False
            for line_number, line in enumerate(lines):
                if content in line:
                    lines[line_number] = content+"\n"
                    found = True
                    break
            if not found:
                lines.append(content+"\n")
            with open(path, "w+") as fe:
                fe.writelines(lines)
            if block :
                if found:#添加成功
                    message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>添加失败喵")
                else :
                    message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>添加成功喵")
    elif t == "2":
        new = ""
        Found = False
        with open(path, "r") as f :
            F =f.readlines()    
            for line in F:
                line =line.strip()
                if line!= content:
                    new +=line
                    new +="\n"
                else :
                    Found=True
        with open(path, "w") as f :
            f.writelines(new);  
        if  Found   :
            message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>删除成功喵")
        else:
            message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>删除失败喵")
    else   : 
        try:
            with open(path, "r") as f:
                line  = ''.join(f.readlines())
                line  = line.lstrip()
                if line :
                    message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>喵\n{line}")
                else:
                    message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>喵~没有哦")
        except:
            message_create(msg['guild']['id'],f"<at id='{msg['user']['id']}'/>喵~没有哦")
    return None