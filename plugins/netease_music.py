import json
import os
import urllib.parse
from hashlib import md5
from random import randrange
import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from sender import send_message
from matcher import plugin_registry, load_trigger

def HexDigest(data):
    # Digests a `bytearray` to a hex string
    return "".join([hex(d)[2:].zfill(2) for d in data])

def HashDigest(text):
    # Digests 128 bit md5 hash
    HASH = md5(text.encode("utf-8"))
    return HASH.digest()

def HashHexDigest(text):
    """Digests 128 bit md5 hash,then digest it as a hexstring"""
    return HexDigest(HashDigest(text))

def parse_cookie(text: str):
    cookie_ = [item.strip().split('=', 1) for item in text.strip().split(';') if item]
    cookie_ = {k.strip(): v.strip() for k, v in cookie_}
    return cookie_

# 输入id选项
def ids(ids):
    if 'music.163.com' in ids:
        index = ids.find('id=') + 3
        ids = ids[index:].split('&')[0]
    return ids

#转换文件大小
def size(value):
     units = ["B", "KB", "MB", "GB", "TB", "PB"]
     size = 1024.0
     for i in range(len(units)):
         if (value / size) < 1:
             return "%.2f%s" % (value, units[i])
         value = value / size
     return value

#转换音质
def music_level1(value):
    if value == 'standard':
        return "标准音质"
    elif value == 'exhigh':
        return "极高音质"
    elif value == 'lossless':
        return "无损音质"
    elif value == 'hires':
        return "Hires音质"
    elif value == 'sky':
        return "沉浸环绕声"
    elif value == 'jyeffect':
        return "高清环绕声"
    elif value == 'jymaster':
        return "超清母带"
    else:
        return "未知音质"

def post(url, params, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
        'Referer': '',
    }
    cookies = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!"
    }
    cookies.update(cookie)
    response = requests.post(url, headers=headers, cookies=cookies, data={"params": params})
    return response.text

def read_cookie():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_file = os.path.join(script_dir, 'cookie.txt')
    with open(cookie_file, 'r') as f:
        cookie_contents = f.read()
    return cookie_contents


def Music(song_ids,level):

    #网易云账号cookie
    cookies = parse_cookie("MUSIC_U=0012BBCE9052459B9E5656133D8E7699AF08420BBB580E2243B60112B1AD9633E688FEC96C4667FC806736915CB9D0DD7B694C7FDD24879001F68B89EA3FB4EF09FD031C234DB127EC9CCABE839451B0E0B71B42F27A1B782D702B54BBD9EDE015881AA0F38889CC00AF3FC1AE41DD13709C1AB0F6D0C5452C3D2F0AC619D755D0EEE4FE1127C89EE1DAEFFF3CC2D9A1DB141FCB1C3C18B7AAE836ED3424B32DBE6C7BD243805ADE876AEB512F5B48B340D44F70BD9C14FD8116C28BF2368B7D07CBE7631FA0021AC66B094E09188F8F1C3B5EA0945BAA28D4D2FA87A07E48465178D3ED0F954F734708D0F993BC1216790676DD032814D5FBF0B3CB10DC28A76D2352A492CBCFD73355B3A45084B949DE70FCB375344BF6A2607494477CAAC1DD6E85C4180BA52A71FEC74B214C210D3BB67A953E37C462890FD261F3999860DC314A091C84CB49E34BCEFE8CA766D2627855FFE6AFC32CD1674812AE34F4A2EE045AB7A3964B3C84DE2BCA9B36CC97BE;appver=8.9.75;")

    url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    AES_KEY = b"e82ckenh8dichen8"
    config = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!",
        "requestId": str(randrange(20000000, 30000000))
    }

    payload = {
        'ids': [ids(song_ids)],
        'level': level,
        'encodeType': 'flac',
        'header': json.dumps(config),
    }

    url2 = urllib.parse.urlparse(url).path.replace("/eapi/", "/api/")
    digest = HashHexDigest(f"nobody{url2}use{json.dumps(payload)}md5forencrypt")
    params = f"{url2}-36cd479b6b5-{json.dumps(payload)}-36cd479b6b5-{digest}"

    # AES-256-ECB PKCS7padding
    padder = padding.PKCS7(algorithms.AES(AES_KEY).block_size).padder()
    padded_data = padder.update(params.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB())
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded_data) + encryptor.finalize()
    params = HexDigest(enc)

    # 发送POST请求
    response = post(url, params, cookies)
    if "参数错误" in response:
        return "解析中参数错误"

    jseg = json.loads(response)
    song_names = "https://music.163.com/api/v3/song/detail"
    data = {'c': json.dumps([{"id":jseg['data'][0]['id'],"v":0}])}
    resp = requests.post(url=song_names, data=data)
    jse = json.loads(resp.text)
    if jseg['data'][0]['url'] is not None:
        if jse['songs']:
            song_url = jseg['data'][0]['url']
            song_name = jse['songs'][0]['name']
            song_picUrl = jse['songs'][0]['al']['picUrl']
            song_alname = jse['songs'][0]['al']['name']
            artist_names = []
            for song in jse['songs']:
                ar_list = song['ar']
                if len(ar_list) > 0:
                    artist_names.append('/'.join(ar['name'] for ar in ar_list))
                song_arname = ', '.join(artist_names)
            return "歌曲名称: " + song_name + "\n封面: <img src='" + song_picUrl + "'/>\n歌手: " + song_arname + "\n专辑: " + song_alname + "\n音质: " + music_level1(jseg['data'][0]['level']) + "\n大小: " + size(jseg['data'][0]['size']) + "\n音乐地址: " + song_url
    else:
        return "信息获取不完整！"

def ncm(msg, sc):
    if len(sc) == 1:
        songid = sc[0]
        lvl = "standard"
    elif len(sc) == 2:
        songid = sc[0]
        if(sc[1]=="2"):
            lvl = "exhigh"
        elif(sc[1]=="3"):
            lvl = "lossless"
        else:
            lvl = "standard"
    else:
        send_message(msg["cid"], "请确保你输入了一项[id]或两项[id]+[音质]")
        return
    result = Music(songid, lvl)
    send_message(msg["cid"], str(result))


def search_from_api(songname):
    try:
        #你需要在本地部署nodejs网易云api
        link = "http://127.0.0.1:3000/search?keywords=" + songname + "&limit=10"
        songs = requests.get(link, timeout=20).text
    except:
        return "搜索失败！"
    songs = json.loads(songs)
    if (songs["code"] == 200):
        if ("songs" in songs["result"].keys()):
            songs = songs["result"]["songs"]
            i = 1
            result = "搜到的歌:\n"
            for song in songs:
                result = result + str(i) + " " + song["name"] + "-" + song["artists"][0]["name"] + " # " + str(
                    song["id"]) + "\n"
                i = i + 1
            return result + "可以用/ncm [id]来获取链接！"
        else:
            return "未搜索到结果"
    else:
        return "搜索失败: " + str(songs["code"])

def search(msg, sc):
    if sc:
        songname = msg["content"].lstrip("/song ").lstrip("/搜歌 ")
        result = search_from_api(songname)
        send_message(msg["cid"], str(result))
    else:
        send_message(msg["cid"], "请使用/song [歌名]来搜索")

def loads():
    plugin_registry(name="ncm", discription="网易云音乐解析", usage="/ncm [id] ([音质])\n/song [歌名]\n/搜歌 [歌名]", status=True)
    load_trigger(name="ncm", type="cmd", func=ncm, trigger="ncm", permission="all")
    load_trigger(name="ncm", type="cmd", func=search, trigger="song", permission="all")
    load_trigger(name="ncm", type="cmd", func=search, trigger="搜歌", permission="all")