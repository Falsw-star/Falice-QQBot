from sender import ssend
from db import database
from plugins.WTE import item_append

def main(msg, data):
    player_data = data['player_data'][msg['user']['id']]
    a_cup_of_water = {
        "WTE_ITEM_INFO": {
            "type": 4,
            "description": "一杯干净透亮的水。冒出的蒸汽让你心情舒畅。",
            "name": "一杯水",
            "hunger": 0,
            "spirit": 5
        }
    }
    location = player_data['location']
    location.append(player_data["name"])
    location.append("背包")
    item_append("一杯水", a_cup_of_water, location)
    ssend(msg["cid"], "一杯热水已经添加到你的背包。")