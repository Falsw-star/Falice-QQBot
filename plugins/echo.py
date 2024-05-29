from matcher import load_trigger, plugin_registry
from sender import ssend

#要运作的函数
def main(msg, special_content):
    if special_content:
        text = ""
        for arg in special_content:
            text += arg + " "
        text = text.strip()
        ssend(msg["guild"]["id"], text)

def loads():
    #注册插件名
    plugin_registry(name="echo", usage="/echo [文本]",status=True)
    #在插件名下注册触发器
    load_trigger(name="echo", type="cmd", func=main, trigger="echo", permission="not_self")