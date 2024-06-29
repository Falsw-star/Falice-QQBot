# Websocket连接的地址
WSBASE = "ws://localhost:5500/v1/events"

# HttpAPI地址
HTTPBASE = "http://localhost:5500/v1/"

# 主时钟周期（这决定了你的机器人多长时间进行一次状态更新和事件处理）
MAINCLOCK = 0.2

# (如果有需要)机器人平台需要的token
PLATFORMTOKEN = "1ab98aa24bc602323851dbf82fd273af1907c0e39c06c1e04e1907aff4320c05"

# 你的权限库
# 键可以作为一个权限组，你可以直接在插件里用，值是一个列表，列表中的元素是用户ID
PERMISSIONS = {
    "all" : "这里只是想告诉你，触发器的默认权限组是all！", #因为“all”的触发器不会来这里匹配权限
    "superusers": ["1145141919810", "2538523045", "3691365980"]
    }

# cmd触发器前面的指令标
CMDSYMBOL = "/"

# 是否制作每个聊天的日志文件（这会记录机器人收到的每一条信息）
MAKELOG = False