# Websocket连接的地址
WSBASE = "ws://127.0.0.1:5500/v1/events"

# HttpAPI地址
HTTPBASE = "http://127.0.0.1:5500/v1/"

# (如果有需要)机器人平台需要的token
PLATFORMTOKEN = "d003b6c251a03919984396e35b5d324b924a2494c3c122c9ad6b56760681dcdd"

# 你的权限库
# 键可以作为一个权限组，你可以直接在插件里用，值是一个列表，列表中的元素是用户ID
PERMISSIONS = {
    "all" : "这里只是想告诉你，触发器的默认权限组是all！", #因为“all”的触发器不会来这里匹配权限
    "superusers": ["1145141919810", "2538523045"]
    }