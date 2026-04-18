import requests
import time
import random
import string
import re

# ========= 工具函数 =========

def gen_device_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=33))  #配置设备id

def gen_request_id():
    return ''.join(random.choices(string.ascii_lowercase, k=19))  #配置请求id

def log(resp, tag=""):
    try:
        print(f"\n===== {tag} =====")
        print(resp.text)
    except:
        print(resp)

# ========= 1. 获取手机号 =========

def get_phone():
    url = "http://api.d1jiema.com/zc/data.php"
    params = {
        "code": "getPhone",
        "token": "",
        "keyWord": "%e8%bf%91%e8%81%94%e6%97%b6%e7%a9%ba",
        "phone": "",
        "cardType": "实卡"
    }
    resp = requests.get(url, params=params)
    log(resp, "获取手机号")
    return resp.text.strip()

# ========= 2. 发送短信 =========

def send_sms(phone):
    url = "https://api.nearlinktech.com/api/v1/auth/send-sms"

    headers = {
        "accept": "application/json, text/plain, */*",
        "x-client-platform": "android",
        "x-client-version": "1.0.0",
        "x-request-id": gen_request_id(),
        "x-device-id": gen_device_id(),
        "Content-Type": "application/json",
        "User-Agent": "okhttp/4.12.0"
    }

    data = {
        "phone": phone,
        "type": "auth"
    }

    resp = requests.post(url, headers=headers, json=data)
    log(resp, "发送短信")

# ========= 3. 获取验证码 =========

def get_code(phone):
    url = "http://api.d1jiema.com/zc/data.php"

    for i in range(4):
        time.sleep(5)

        params = {
            "code": "getMsg",
            "token": "",
            "phone": phone,
            "keyWord": "近联时空"
        }

        resp = requests.get(url, params=params)
        log(resp, f"获取验证码 第{i+1}次")

        text = resp.text

        # 提取6位验证码
        match = re.search(r'验证码.*?(\d{6})', text)
        if match:
            return match.group(1)

    return None

# ========= 4. 登录 =========

def login(phone, code):
    url = "https://api.nearlinktech.com/api/v1/auth/sms-login"

    headers = {
        "accept": "application/json, text/plain, */*",
        "x-client-platform": "android",
        "x-client-version": "1.0.0",
        "x-request-id": gen_request_id(),
        "x-device-id": gen_device_id(),
        "x-install-channel": "oppo",
        "Content-Type": "application/json",
        "User-Agent": "okhttp/4.12.0"
    }

    data = {
        "phone": phone,
        "code": code,
        "device_type": "OnePlus Ace 5 OnePlus PKG110",
        "os_platform": "Android",
        "os_version": "15"
    }

    resp = requests.post(url, headers=headers, json=data)
    log(resp, "登录并提取CK")

    try:
        return resp.json()["data"]["token"]["access_token"]
    except:
        return None

# ========= 5. 提取CK =========

def run_tasks(token):
    base_headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "User-Agent": "okhttp/4.12.0"
    }

    request_id = gen_request_id()

    def headers(extra={}):
        h = base_headers.copy()
        h.update({
            "x-request-id": request_id,
            "x-device-id": gen_device_id()
        })
        h.update(extra)
        return h

    # ===== 任务一：开始广播 =====
    resp1 = requests.post(
        "https://api.nearlinktech.com/api/v1/broadcast/start",
        headers=headers({"Content-Type": "application/json"}),
        json={
            "screens":[{"type":"text","content":"1"}],
            "duration":"168",
            "scope":1,
            "location":"120.36256757015629,30.313401754170805"
        }
    )
    log(resp1, "1.广播任务")

    # =====任务二：签到 =====
    resp2 = requests.post(
        "https://www.nearlinktech.com:10089/api/v1/space/checkin",
        headers=headers({"Content-Type": "application/json"}),
        json={
            "activity_id":"432484537503715328",
            "location":"120.35519307,30.31613841"
        }
    )
    log(resp2, "2.签到任务")
    # ===== 任务三：点赞广播 =====
    resp_like = requests.post(
        "https://api.nearlinktech.com/api/v1/interaction/like/broadcast/434901157228322816",
        headers=headers(),
    )
    log(resp_like, "3.点赞广播任务")

    # ===== 任务四：附近的推荐 =====
    resp_around = requests.post(
        "https://api.nearlinktech.com/api/v1/recommend/around",
        headers=headers({
            "accept": "application/json, text/plain, */*",
            "x-client-platform": "android",
            "x-client-version": "1.0.0",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/4.12.0"
        }),
        json={
            "nearby_bids": [],
            "page": 1,
            "size": 10,
            "lat": 30.31570822,
            "lng": 120.35798377
        }
    )
    log(resp_around, "4.附近推荐")
    # ===== 任务五：获取任务列表 =====
    resp_task = requests.get(
        "https://www.nearlinktech.com:10089/api/v1/task",
        headers=headers({
            "X-Client-Platform": "h5",
            "X-Requested-With": "com.nearlinktech.jijin",
            "Referer": "https://www.nearlinktech.com:10089/novice-experience?jijin_id=hg2idsxx&activity_id=432484537503715328"
        }),
        params={
            "activity_id": "432484537503715328"
        }
    )
    log(resp_task, "5.读取任务列表")
    # ===== 任务六：Beacon 遇见 =====
    resp_beacon = requests.post(
        "https://api.nearlinktech.com/api/v1/beacons/meets",
        headers=headers({"Content-Type": "application/json"}),
        json={
            "beacons": [{
                "bid": "ZKQIfpC1JixEt0OX",
                "created_at": int(time.time() * 1000),
                "meet_at": int(time.time() * 1000),
                "meet_location_latitude": 30.31576843,
                "meet_location_longitude": 120.3579694,
                "rssi_max": -63,
                "tx_power": 127,
                "updated_at": int(time.time() * 1000),
                "updated_location_latitude": 30.31576843,
                "updated_location_longitude": 120.3579694,
                "updated_rssi": -58
            }]
        }
    )
    log(resp_beacon, "6.Beacon遇见")

    time.sleep(2)

     # ===== 领取奖励 =====
    resp3 = requests.post(
        "https://www.nearlinktech.com:10089/api/v1/task/1/receive",
        headers=headers({"Content-Type": "application/json"}),
        json={"activity_id":"432484537503715328"}
    )
    log(resp3, "领取奖励")


    # ===== 获取奖品列表 =====
    resp4 = requests.get(
        "https://www.nearlinktech.com:10089/api/v1/referral/prizes?activity_id=432484537503715328",
        headers=headers()
    )
    log(resp4, "获取奖品列表")

    # 提取 redeem_code
    try:
        data = resp4.json()
        items = data["data"]["items"]
        redeem_code = items[0]["redeem_code"]

        print("\n🎉 获取到券码:", redeem_code)

        with open("redeem_code.txt", "a") as f:
            f.write(redeem_code + "\n")

    except Exception as e:
        print("提取 redeem_code 失败:", e)


# ========= 主流程 =========

def main():
    while True:
        phone = get_phone()
        if not phone:
            continue

        send_sms(phone)

        print("等待15秒...")
        time.sleep(15)

        code = get_code(phone)

        if not code:
            print("❌ 未获取到验证码，重新开始")
            continue

        print("验证码:", code)

        token = login(phone, code)

        if not token:
            print("❌ 登录失败，重新开始")
            continue

        print("✅ 登录成功")
        # ===== 保存 CK =====
        with open("ck.txt", "a", encoding="utf-8") as f:
            f.write(token + "\n")

        print("💾 CK已保存:", token)

        run_tasks(token)

        print("==== 完成一轮 ====\n")


if __name__ == "__main__":
    main()
