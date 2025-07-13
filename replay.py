import requests
import time
import os
from datetime import datetime

cookie = os.getenv("CK")
if not cookie:
    print("❌ CK 环境变量未设置。请在 GitHub Secrets 中配置")
    exit(1)

headers = {
    "Host": "api.m.jd.com",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://laputa.jd.com",
    "User-Agent": "jdapp;iPhone;15.1.70;;;M/5.0;...",
    "Referer": "https://laputa.jd.com/",
    "Cookie": cookie
}

data = 'body=...&appid=laputa&functionId=mb2capp_sports_exchangeHealthCoins&...'

def is_within_valid_period():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    return 0 <= hour <= 7 and (minute >= 58 or minute <= 3)

def main():
    if not is_within_valid_period():
        print("⏳ 当前不在执行时间段内，程序退出。")
        return

    print("✅ 开始发送请求（每秒两次，持续5分钟）")
    for _ in range(300):
        for _ in range(2):
            try:
                resp = requests.post("https://api.m.jd.com/api?functionId=mb2capp_sports_exchangeHealthCoins", headers=headers, data=data, timeout=5)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 状态码：{resp.status_code}")
            except Exception as e:
                print("请求异常：", e)
        time.sleep(1)

if __name__ == "__main__":
    main()
