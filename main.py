import requests
import os
import json
import time
import random

# ===== 环境变量 =====
COOKIE = os.environ.get("COOKIE")
FRIEND_UID_STR = os.environ.get("FRIEND_UID", "")
SEND_CONTENT = os.environ.get("SEND_MSG", "")

FRIEND_UID_LIST = [uid.strip() for uid in FRIEND_UID_STR.split(",") if uid.strip()]

BASE_URL = "https://www.douyin.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": BASE_URL,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# ===== 工具函数 =====

def human_sleep(a=3, b=10):
    t = random.uniform(a, b)
    print(f"⏱️ 等待 {t:.2f} 秒")
    time.sleep(t)


def safe_request(method, url, **kwargs):
    for i in range(3):
        try:
            if method == "GET":
                res = requests.get(url, timeout=10, **kwargs)
            else:
                res = requests.post(url, timeout=10, **kwargs)

            if res.status_code == 200:
                return res.json()
            else:
                print(f"⚠️ 状态码异常: {res.status_code}")

        except Exception as e:
            print(f"⚠️ 请求失败({i+1}/3): {e}")

        time.sleep(random.randint(2, 6))
    return None


def get_ac_nonce():
    print("🔐 获取 ac_nonce...")
    res = requests.get(BASE_URL, headers=HEADERS)
    return res.cookies.get("ac_nonce", "")


# ===== 核心功能 =====

def send_text_message(friend_uid, nonce):
    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": friend_uid,
        "content": SEND_CONTENT,
        "ac_nonce": nonce,
    }

    result = safe_request("POST", url, headers=HEADERS, data=data)

    print(f"\n📨 发消息 → {friend_uid}")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result and result.get("status_code") == 0


def get_latest_video(friend_uid, nonce):
    url = f"{BASE_URL}/aweme/v1/user/post/aweme/"
    params = {
        "user_id": friend_uid,
        "count": 1,
        "ac_nonce": nonce
    }

    result = safe_request("GET", url, headers=HEADERS, params=params)

    if not result or not result.get("aweme_list"):
        print(f"❌ 未获取到视频: {friend_uid}")
        return None

    aweme_id = result["aweme_list"][0]["aweme_id"]
    print(f"🎬 获取视频ID: {aweme_id}")
    return aweme_id


def send_video(friend_uid, aweme_id, nonce):
    if not aweme_id:
        return False

    url = f"{BASE_URL}/aweme/v1/im/message/send/"
    data = {
        "to_user_id": friend_uid,
        "aweme_id": aweme_id,
        "content": "分享作品",
        "ac_nonce": nonce,
    }

    result = safe_request("POST", url, headers=HEADERS, data=data)

    print(f"\n📤 转发视频 → {friend_uid}")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result and result.get("status_code") == 0


# ===== 主流程 =====

if __name__ == "__main__":
    print("🚀 自动任务启动")
    print(f"👥 好友数量: {len(FRIEND_UID_LIST)}")

    if not COOKIE:
        print("❌ COOKIE 未设置，终止")
        exit()

    nonce = get_ac_nonce()
    if not nonce:
        print("❌ 获取 nonce 失败")
        exit()

    for uid in FRIEND_UID_LIST:
        print(f"\n====== 处理好友 {uid} ======")

        human_sleep()

        send_text_message(uid, nonce)

        human_sleep()

        vid = get_latest_video(uid, nonce)

        human_sleep()

        send_video(uid, vid, nonce)

        human_sleep(5, 15)

    print("\n✅ 全部任务完成")
