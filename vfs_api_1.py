import os
import tls_client
import pandas as pd
from dotenv import load_dotenv
from capsolver import cloudflare_solver
from encryption import encrypt_rsa
from proxy import active_proxies


load_dotenv()

# Constants
PROXIES_LIST = [
    # 'geo.iproyal.com:12321:letinnow:nowwearefreetoin_country-pt_streaming-1',
    # 'eu.vf8bp1jd.lunaproxy.net:12233:user-lu8799918-region-pt:Tixa4ever',
    '64.137.60.43:5107:csboqgsx:45j53sy19zg5'
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


# Utility functions
def update_headers(auth_token):
    cokie_value = "; ".join([f"{key}={value}" for key, value in session.cookies.items()])
    HEADERS.update({
        'Authorize': auth_token,
        'Cookie': cokie_value,
        'Route': f'{C_CODE}/en/{D_CODE}'
    })


# API Calls
def login(captcha_token, email, password):
    response = session.post(
        url='https://lift-api.vfsglobal.com/user/login',
        headers=HEADERS,
        json={
            'username': email,
            'password': password,
            'missioncode': D_CODE,
            'countrycode': C_CODE,
            'languageCode': 'en-US',
            'captcha_version': 'cloudflare-v1',
            'captcha_api_key': captcha_token
        }
    )
    print(f"\nLogin Status Code:", response.status_code)
    if response.status_code == 200:
        auth_token = response.json()["accessToken"]
        update_headers(auth_token)
        print('Login Response:', response.content)
    else:
        print("Login failed.")


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
        login(captcha_token, EMAIL, encrypted_password)

    except Exception as e:
        print(f"Error using proxy {proxy_url}: {e}")


def main():

    # Uncomment below 2 line to read all proxy from txt file
    # with open('proxies.txt', 'r') as file:
    #     working_proxies = [line.strip() for line in file.readlines()]

    # Uncomment below line to read proxy from proxy list above in code
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
