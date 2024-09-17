import os
import time
import tls_client
import pandas as pd
from dotenv import load_dotenv
from capsolver import cloudflare_solver
from encryption import encrypt_rsa
from proxy import active_proxies


load_dotenv()

# Constants
PROXIES_LIST = [
    'geo.iproyal.com:12321:letinnow:nowwearefreetoin_country-pt_streaming-1',
    # 'eu.vf8bp1jd.lunaproxy.net:12233:user-lu8799918-region-pt:Tixa4ever',
    # '45.151.162.198:6600:bxuzrwgx:lbvnmybo6jez',
    # '206.41.172.74:6634:bxuzrwgx:lbvnmybo6jez'
]

C_CODE = 'cpv'
D_CODE = 'prt'
PAGE_URL = f"https://visa.vfsglobal.com/{C_CODE}/en/{D_CODE}/login"
CENTER_CODE = 'PRPR'
VISA_CATEGORY = 'fmv'
HEADERS = {'Referer': 'https://visa.vfsglobal.com/'}

EMAIL = os.getenv('EMAIL')

# Initialize session
session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

session.verify = True

# Utility functions
def update_headers(auth_token):
    cookie_value = "; ".join([f"{key}={value}" for key, value in session.cookies.items()])
    HEADERS.update({
        'Authorization': f'{auth_token}',
        'Cookie': cookie_value,
        'Route': f'{C_CODE}/en/{D_CODE}'
    })


# API Calls
def login(captcha_token, email, password, otp_code):
    response = session.post(
        url='https://lift-api.vfsglobal.com/user/login',
        headers=HEADERS,
        data={
            'username': email,
            'password': password,
            'missioncode': D_CODE,
            'countrycode': C_CODE,
            'languageCode': 'en-US',
            'captcha_version': 'cloudflare-v1',
            'captcha_api_key': captcha_token,
            'otp': otp_code
        }
    )
    print(f"\nLogin Status Code:", response.status_code)
    if response.status_code == 200:
        auth_token = response.json()["accessToken"]
        update_headers(auth_token)
        print('Login Response:', response.content)
    else:
        print("Login failed.")


def check_applications():
    response = session.post(
        url='https://lift-api.vfsglobal.com/appointment/application',
        headers=HEADERS,
        json={
            'countryCode': C_CODE,
            'missionCode': D_CODE,
            'loginUser': EMAIL,
            'languageCode': 'en-US'
        }
    )
    print(f"\nApplication Status Code:", response.status_code)
    print(f"\nApplication Response:", response.content)
    if response.status_code == 200:
        print('Application Response:', response.content)
        data = response.json().get('data')
        if data:
            urn = data[0].get('urn')
            print(f"\nApplied Application : {urn}")
            return urn


def check_available_slot():
    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/CheckIsSlotAvailable",
        headers=HEADERS,
        json={
            "countryCode": C_CODE,
            "missionCode": D_CODE,
            "loginUser": EMAIL,
            "payCode": "",
            "roleName": "Individual",
            "vacCode": CENTER_CODE,
            "visaCategoryCode": VISA_CATEGORY
        }
    )
    print(f"\nSlot Available Status Code:", response.status_code)
    # print(f"\nSlot Available Response:", response.content)
    if response.status_code == 200:
        print('Slot Available Response:', response.content)


# Proxy handling
def use_proxy(proxy, captcha_token, encrypted_password):
    ip, port, user, password = proxy.split(':')
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    session.proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    print(f"\nUsing proxy: {proxy_url}")

    try:

        # otp_code = input("Enter OTP code: ")
        otp_code = "482666"
        login(captcha_token, EMAIL, encrypted_password, otp_code)

        '''Here you can check headers and cookies after login success'''
        print(HEADERS)
        time.sleep(5)
        print("------------------------")
        print(session.client_identifier)
        print(session.cookies)
        print(session.headers)
        print(session.params)
        session.headers.update({'Content-Type': 'application/json'})
        print(session.headers)
        print("--------------------------")

        check_applications()
        check_available_slot()

    except Exception as e:
        print(f"Error using proxy {proxy_url}: {e}")


def main():
    working_proxies = active_proxies(PROXIES_LIST)
    encrypted_password = encrypt_rsa()

    captcha_result = cloudflare_solver(PAGE_URL)
    if not captcha_result:
        print("Captcha solving failed.")
        return

    captcha_token = captcha_result.get("token")
    print('Captcha_Result:', captcha_result)

    for proxy in working_proxies:
        use_proxy(proxy, captcha_token, encrypted_password)


if __name__ == "__main__":
    main()
