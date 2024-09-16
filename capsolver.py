import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

SITE_KEY = os.getenv('SITE_KEY')
CAPSOLVER_API_KEY = os.getenv('CAPSOLVER_API_KEY')


def cloudflare_solver(PAGE_URL):
    data = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": PAGE_URL,
            "websiteKey": SITE_KEY,
            "metadata": {"action": "login"}
        }
    }
    uri = 'https://api.capsolver.com/createTask'
    res = requests.post(uri, json=data)
    resp = res.json()
    task_id = resp.get('taskId')
    if not task_id:
        print("Failed taskId:", res.content)
        return
    print('Created taskId:', task_id)
    while True:
        time.sleep(1)
        data = {
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id
        }
        response = requests.post('https://api.capsolver.com/getTaskResult', json=data)
        resp = response.json()
        status = resp.get('status', '')
        if status == "ready":
            print(f"\nCaptcha success:", response.status_code)
            return resp.get('solution')
        if status == "failed" or resp.get("errorId"):
            print("failed! => ", response.content)
            return None


if __name__ == '__main__':
    c_code = 'npl'
    d_code = 'jpn'

    PAGE_URL = f"https://visa.vfsglobal.com/{c_code}/en/{d_code}/login"

    captcha_result = cloudflare_solver(PAGE_URL)
    if not captcha_result:
        print("Captcha solving failed.")

    captcha_token = captcha_result.get("token")
    print('Captcha_Result: ', captcha_result)

