# item type:
# -2 门
# -1 环境(environment)
# 0 玩家(player)
# 1 背包(backpack)
# 2 坐垫(seat)（如沙发等）
# 3 可交互物体(object)
# 4 食物(food)
# 5 信息类物品(不可使用)


test_玩家 = {
    "WTE_ITEM_INFO": {
        "type": 0,
        "name": "我喜欢小一qwq",
        "description": "一位蓝色星球上的旅人。",
        "user_id": "11111111"
    }
}

test_门 = {
    "WTE_ITEM_INFO": {
        "type": -2,
        "name": "门",
        "description": "一个门。",
        "target": ["测试聊天室"],
        "targeted" : "看起来你回到了原来的地方。"
    }
}

饮水机 =  {
    "WTE_ITEM_INFO": {
        "type": 3,
        "description": "可以在这里接水。",
        "name": "饮水机",
        "acts": {
            "接水": "wte_water_dispenser"
        }
    }
}