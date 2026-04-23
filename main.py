import requests
import os
import json
import time
import random  # 1. 引入 random 库，用于随机选择

# 自动读取GitHub私密变量
COOKIE = os.environ.get("COOKIE")
# 多好友：这里会自动读取逗号隔开的所有好友ID
FRIEND_UID_STR = os.environ.get("FRIEND_UID")
# 读取所有备选内容（在GitHub Secrets中用英文逗号隔开）
RAW_CONTENT_STR = os.environ.get("SEND_MSG") 

# 2. 处理随机内容逻辑
# 将字符串按逗号分割成列表，并去除首尾空格
content_list = [x.strip() for x in RAW_CONTENT_STR.split(",") if x.strip()]
# 从列表中随机选择一个作为今天的发送内容
SEND_CONTENT = random.choice(content_list) if content_list else "✨"

# 分割字符串，拆分出每一个好友的UID
FRIEND_UID_LIST = [uid.strip() for uid in FRIEND_UID_STR.split(",") if uid.strip()]

# 抖音网页版官方接口基础配置
BASE_URL = "https://www.douyin.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": BASE_URL,
}

def get_ac_nonce():
    # 全自动实时获取最新ac_nonce，永久解决cookie鉴权过期问题
    resp = requests.get(BASE_URL, headers=HEADERS)
    nonce = resp.cookies.get("ac_nonce", "")
    print(f"✅ 成功获取最新ac_nonce: {nonce}")
    return nonce

def send_text_message(friend_uid):
    # 给单个好友发送固定消息/表情，纯火花互动，无AI自动回复
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": friend_uid,
        "content": SEND_CONTENT, # 这里会使用上面随机选出的内容
        "ac_nonce": nonce,
    }
    res = requests.post(url, headers=HEADERS, data=data)
    result = res.json()
    print(f"\n===== 给好友【{friend_uid}】发送内容: {SEND_CONTENT} =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status_code") == 0:
        print(f"🎉 好友{friend_uid} 消息发送成功，火花互动触发完成！")
        return True
    else:
        print(f"❌ 好友{friend_uid} 消息发送失败")
        print("失败原因：", result.get("status_msg", "未知错误"))
        return False

def get_user_latest_video(friend_uid):
    # 获取单个好友最新发布的作品视频
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/user/post/aweme/"
    params = {
        "user_id": friend_uid,
        "count": 1,
        "ac_nonce": nonce
    }
    res = requests.get(url, headers=HEADERS, params=params)
    data = res.json()
    if data.get("status_code") != 0 or not data.get("aweme_list"):
        print(f"❌ 好友{friend_uid} 未获取到最新视频")
        return None
    latest_aweme = data["aweme_list"][0]
    aweme_id = latest_aweme["aweme_id"]
    print(f"✅ 好友{friend_uid} 获取到最新视频ID: {aweme_id}")
    return aweme_id

def send_video_card(friend_uid, aweme_id):
    # 把单个好友最新视频转发到私信
    if not aweme_id:
        return False
    nonce = get_ac_nonce()
    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": friend_uid,
        "aweme_id": aweme_id,
        "content": "分享作品",
        "ac_nonce": nonce,
    }
    res = requests.post(url, headers=HEADERS, data=data)
    result = res.json()
    print(f"\n===== 好友【{friend_uid}】视频转发结果 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status_code") == 0:
        print(f"🎉 好友{friend_uid} 最新视频转发私信成功！")
        return True
    else:
        print(f"❌ 好友{friend_uid} 视频转发失败")
        print("失败原因：", result.get("status_msg", "未知错误"))
        return False

if __name__ == "__main__":
    print("===== 抖音多好友自动续火脚本启动 =====")
    print(f"本次待执行任务好友总数：{len(FRIEND_UID_LIST)} 个")
    print(f"今日随机池内容: {content_list}")
    print(f"🎲 系统抽取结果: {SEND_CONTENT}")
    print("-"*50)
    # 循环遍历你填写的每一个好友，逐个执行全部任务
    for friend_uid in FRIEND_UID_LIST:
        print(f"\n>>>>>>>>>> 开始处理好友：{friend_uid}")
        time.sleep(1)
        send_text_message(friend_uid)
        time.sleep(2)
        vid = get_user_latest_video(friend_uid)
        send_video_card(friend_uid, vid)
        print(f"\n========== 好友 {friend_uid} 全部任务完成 ==========")
        time.sleep(3) # 好友之间加间隔，避免接口风控限制
    print("\n" + "="*60)
    print("✅ 全部好友 每日自动任务全部执行完毕！")
