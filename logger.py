import time

def paint(text, color):
    if color == "green":
        return f"\033[1;32m{text}\033[0m"
    elif color == "red":
        return f"\033[1;31m{text}\033[0m"
    elif color == "yellow":
        return f"\033[1;33m{text}\033[0m"
    elif color == "blue":
        return f"\033[1;36m{text}\033[0m"
    elif color == "purple":
        return f"\033[1;35m{text}\033[0m"

#向终端打印LOGGER中的信息
def log(content, level: str = "INFO"):
    content = str(content)
    if level == "SUCCESS":
        tag = "[" + str(paint(level, "green")) + "]"
        content = str(paint(content, "green"))
    elif level == "WARNING":
        tag = "[" + str(paint(level, "red")) + "]"
        content = str(paint(content, "red"))
    elif level == "DEBUG":
        tag = "[" + str(paint(level, "purple")) + "]"
    elif level == "INFO":
        tag =  "[" + str(paint(level, "blue")) + "]"
    elif level == "CHAT":
        tag = "[" + str(paint(level, "yellow")) + "]"
    else:
        tag = level
    print(tag + " : " + content)

def save(msg):
     with open("logs/" + msg["guild"]["name"] + '-' + msg["cid"] + '.log', "a") as f:
        f.write("\n[" + time.asctime() + "]" + msg["user"]["name"] + "(" + msg["user"]["id"] + ") : " + msg["content"])
        f.close()
     