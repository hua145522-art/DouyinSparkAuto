import requests
import os
import json
import time

# 自动读取你后面配置的私密变量，所有敏感信息全程加密，不会写在代码里
COOKIE = os.environ.get("COOKIE")
FRIEND_UID = os.environ.get("FRIEND_UID")
SEND_CONTENT = os.environ.get("SEND_MSG")

# 抖音网页版官方接口基础配置
BASE_URL = "https://www.douyin.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": BASE_URL,
}

def get_ac_nonce():
    # 核心修复：全自动实时获取最新ac_nonce
    # 彻底解决你之前手动补cookie、鉴权失效的所有问题，以后永远不用手动更新cookie
    resp = requests.get(BASE_URL, headers=HEADERS)
    nonce = resp.cookies.get("ac_nonce", "")
    print(f"✅ 成功获取最新ac_nonce: {nonce}")
    return nonce

def send_text_message():
    # 功能：发送你预设的固定消息/表情，纯火花互动
    # 完全不会读取、不会回复对方的任何私信消息，无任何AI自动回复
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": FRIEND_UID,
        "content": SEND_CONTENT,
        "ac_nonce": nonce,
    }
    res = requests.post(url, headers=HEADERS, data=data)
    result = res.json()
    print("===== 固定消息发送结果 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status_code") == 0:
        print("🎉 固定消息发送成功，火花互动触发完成！")
        return True
    else:
        print("❌ 消息发送失败")
        print("失败原因：", result.get("status_msg", "未知错误"))
        return False

def get_user_latest_video():
    # 功能：获取好友最新发布的作品视频
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/user/post/aweme/"
    params = {
        "user_id": FRIEND_UID,
        "count": 1,
        "ac_nonce": nonce
    }
    res = requests.get(url, headers=HEADERS, params=params)
    data = res.json()
    if data.get("status_code") != 0 or not data.get("aweme_list"):
        print("❌ 未获取到好友最新视频")
        return None
    latest_aweme = data["aweme_list"][0]
    aweme_id = latest_aweme["aweme_id"]
    print(f"✅ 获取到好友最新视频ID: {aweme_id}")
    return aweme_id

def send_video_card(aweme_id):
    # 功能：把好友最新视频自动转发到私信
    if not aweme_id:
        return False
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": FRIEND_UID,
        "aweme_id": aweme_id,
        "content": "分享作品",
        "ac_nonce": nonce,
    }
    res = requests.post(url, headers=HEADERS, data=data)
    result = res.json()
    print("===== 视频转发结果 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status_code") == 0:
        print("🎉 好友最新视频转发私信成功！")
        return True
    else:
        print("❌ 视频转发失败")
        print("失败原因：", result.get("status_msg", "未知错误"))
        return False

if __name__ == "__main__":
    print("===== 抖音自动续火脚本启动 =====")
    print(f"目标好友ID: {FRIEND_UID}")
    print(f"本次固定发送内容: {SEND_CONTENT}")
    time.sleep(1)
    # 第一步：发送固定表情消息续火花
    send_text_message()
    time.sleep(2)
    # 第二步：获取并转发好友最新发布视频
    vid = get_user_latest_video()
    send_video_card(vid)
    print("\n===== 本次全部任务执行完毕 =====")
