from matcher import plugin_registry, load_trigger
from sender import send_message
from logger import log
from db import database, exists

def save_in(msg, special_content):
    if len(special_content) != 3:
        send_message(msg["cid"], "参数错误")
        return
    
    db_name = special_content[0]
    db_key = special_content[1]
    db_content = special_content[2]

    db = database(db_name)
    db.open()
    db.data[db_key] = db_content
    db.save()
    send_message(msg["cid"], f"存储[{db_content}]到[{db_name}][{db_key}]成功")

def check(msg, special_content):
    if len(special_content) != 2:
        send_message(msg["cid"], "参数错误")
        return
    
    db_name = special_content[0]
    db_key = special_content[1]

    if exists(db_name):
        db = database(db_name)
        db.open()
        if db_key in db.data:
            if db.data[db_key]:
                send_message(msg["cid"], str(db.data[db_key]))
            else:
                send_message(msg["cid"], "发不出来xwx")
        else:
            send_message(msg["cid"], f"[{db_name}][{db_key}]不存在")
    else:
        send_message(msg["cid"], f"[{db_name}]不存在")

def loads():
    usage = "/db_save <db_name> <db_key> <db_content>\n/db_check <db_name> <db_key>"
    plugin_registry("db_test", usage=usage, status=True)
    load_trigger("db_test", "cmd", save_in, "db_save", block=True)
    load_trigger("db_test", "cmd", check, "db_check", block=True)