import os
import time
import tls_client
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from capsolver import cloudflare_solver
from encryption import encrypt_rsa
from proxy import active_proxies

load_dotenv()
# Get today's date
today_date = datetime.today()
formatted_date = today_date.strftime("%d/%m/%Y")

# Constants
PROXIES_LIST = [
    # '206.41.172.74:6634:bxuzrwgx:lbvnmybo6jez',
    '206.41.172.74:6634:bxuzrwgx:lbvnmybo6jez',
    # '64.137.60.43:5107:csboqgsx:45j53sy19zg5'
]

C_CODE = 'npl'
D_CODE = 'jpn'
PAGE_URL = f"https://visa.vfsglobal.com/{C_CODE}/en/{D_CODE}/login"
CENTER_CODE = 'JPNPKT'
VISA_CATEGORY = 'VV'
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


def check_applications():
    response = session.post(
        url='https://lift-api.vfsglobal.com/appointment/application',
        headers=HEADERS,
        json={
            "countryCode": C_CODE,
            "missionCode": D_CODE,
            "loginUser": EMAIL,
            "languageCode": "en-US"
        }
    )
    print(f"\nApplication Status Code:", response.status_code)
    if response.status_code == 200:
        print('Application Response:', response.content)
        data = response.json().get('data')
        if data:
            urn = data[0].get('urn')
            print(f"\nApplied Application : {urn}")
            return urn


def delete_application(urn):
    response = session.post(
        url='https://lift-api.vfsglobal.com/appointment/cancel',
        headers=HEADERS,
        json={
            "countryCode": C_CODE,
            "missionCode": D_CODE,
            "loginUser": EMAIL,
            "cultureCode": "en-US",
            "urn": urn
        }
    )
    print(f"\nDelete Status Code:", response.status_code)
    if response.status_code == 200:
        print('Delete Response:', response.content)


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
    if response.status_code == 200:
        print('Slot Available Response:', response.content)


def post_applicants(applicant_data):
    applicant_data = applicant_data.astype(object).where(pd.notnull(applicant_data), None).to_dict()

    payload = {
        "countryCode": C_CODE,
        "missionCode": D_CODE,
        "centerCode": CENTER_CODE,
        "loginUser": EMAIL,
        "visaCategoryCode": VISA_CATEGORY,
        "isEdit": False,
        "applicantList": [{
            "urn": "",
            "arn": "",
            "loginUser": EMAIL,
            "firstName": applicant_data['first_name'],
            "lastName": applicant_data['last_name'],
            "gender": applicant_data['gender'],
            "contactNumber": str(applicant_data['contact_number']),
            "dialCode": str(applicant_data['dial_code']),
            "passportNumber": applicant_data['passport_number'],
            "passportExpirtyDate": applicant_data['passport_expiry'],
            "dateOfBirth": applicant_data['dob'],
            "emailId": applicant_data['email'],
            "nationalityCode": applicant_data['nationality'],
            "referenceNumber": applicant_data['Migris_number'],
            "isAutoRefresh": True
        }],
        "languageCode": "en-US",
        "isWaitlist": False,
        "isMIGRISNumberEnabled": True,
        "juridictionCode": None
    }

    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/applicants",
        headers=HEADERS,
        json=payload
    )
    print(f"\nApplicants Status Code:", response.status_code)
    if response.status_code == 200:
        print('Applicants Response:', response.content)
        urn = response.json().get('urn')
        if urn:
            print(f"\nNew Application: {urn}")
            return urn


def send_otp(urn):
    payload = {
        "urn": urn,
        "loginUser": EMAIL,
        "missionCode": D_CODE,
        "countryCode": C_CODE,
        "centerCode": CENTER_CODE,
        "captcha_version": "",
        "captcha_api_key": "",
        "OTP": "",
        "otpAction": "GENERATE",
        "languageCode": "en-US",
        "userAction": None
    }
    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/applicantotp",
        headers=HEADERS,
        json=payload
    )
    print(f"\nOTP Send Status Code:", response.status_code)
    if response.status_code == 200:
        print('OTP Send Response:', response.content)


def submit_otp(urn, otp_code):
    payload = {
        "urn": urn,
        "loginUser": EMAIL,
        "missionCode": D_CODE,
        "countryCode": C_CODE,
        "centerCode": CENTER_CODE,
        "captcha_version": "",
        "captcha_api_key": "",
        "OTP": otp_code,
        "otpAction": "VALIDATE",
        "languageCode": "en-US",
        "userAction": None
    }
    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/applicantotp",
        headers=HEADERS,
        json=payload
    )
    print(f"\nOTP Submit Status Code:", response.status_code)
    if response.status_code == 200:
        print('OTP Submit Response:', response.content)


def available_dates(urn):
    payload = {
        "urn": urn,
        "loginUser": EMAIL,
        "missionCode": D_CODE,
        "countryCode": C_CODE,
        "centerCode": CENTER_CODE,
        "visaCategoryCode": VISA_CATEGORY,
        "fromDate": formatted_date,
        "payCode": ""
    }
    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/calendar",
        headers=HEADERS,
        json=payload
    )
    print(f"\nAvailable Dates Status Code:", response.status_code)
    if response.status_code == 200:
        print('Available Dates Response:', response.content)
        dates = response.json().get('calendars')
        unique_dates = list({date.get('date') for date in dates})
        active_dates = sorted(
            [datetime.strptime(date, "%m/%d/%Y").strftime("%d/%m/%Y") for date in unique_dates],
            key=lambda x: datetime.strptime(x, "%d/%m/%Y")
        )
        print("Active Dates: ", active_dates)
        return active_dates


def available_times(urn, active_dates):
    date_slot = active_dates[0]
    payload = {
        "urn": urn,
        "loginUser": EMAIL,
        "missionCode": D_CODE,
        "countryCode": C_CODE,
        "centerCode": CENTER_CODE,
        "visaCategoryCode": VISA_CATEGORY,
        "slotDate": date_slot,
    }
    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/timeslot",
        headers=HEADERS,
        json=payload
    )
    print(f"\nAvailable Times Status Code:", response.status_code)
    if response.status_code == 200:
        print('Available Times Response:', response.content)
        timeslots = response.json().get('slots')
        slots = list({slot.get('allocationId') for slot in timeslots})
        print("Slots: ", slots)
        return slots


def schedule_appointment(urn, slots):
    slot = str(slots[0])
    payload = {
        "missionCode": D_CODE,
        "countryCode": C_CODE,
        "centerCode": CENTER_CODE,
        "loginUser": EMAIL,
        "urn": urn,
        "notificationType": "none",
        "paymentdetails": {
            "paymentmode": "Vac",
            "RequestRefNo": "",
            "clientId": "",
            "merchantId": "",
            "amount": 0,
            "currency": None
        },
        "allocationId": slot,
        "CanVFSReachoutToApplicant": True
    }

    response = session.post(
        url="https://lift-api.vfsglobal.com/appointment/schedule",
        headers=HEADERS,
        json=payload
    )
    print(f"\nScheduled Appointment Status Code:", response.status_code)
    if response.status_code == 200:
        print('Scheduled Appointment Response:', response.content)


# Proxy handling
def use_proxy(proxy, captcha_token, encrypted_password, applicant_data):
    ip, port, user, password = proxy.split(':')
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    session.proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    print(f"\nUsing proxy: {proxy_url}")

    try:
        login(captcha_token, EMAIL, encrypted_password)
        urn = check_applications()
        if urn:
            delete_application(urn)
        check_available_slot()
        urn = post_applicants(applicant_data)
        send_otp(urn)
        time.sleep(5)
        otp_code = input("\nEnter OTP Code: ")
        # otp_code = otp_mail()
        submit_otp(urn, otp_code)
        active_dates = available_dates(urn)
        active_slots = available_times(urn, active_dates)
        schedule_appointment(urn, active_slots)

    except Exception as e:
        print(f"Error using proxy {proxy_url}: {e}")


def main():
    applicant_data = pd.read_csv('applicant_details.csv').iloc[1]

    # with open('webshare_proxies.txt', 'r') as file:
    #     working_proxies = [line.strip() for line in file.readlines()]
    working_proxies = active_proxies(PROXIES_LIST)

    encrypted_password = encrypt_rsa()

    captcha_result = cloudflare_solver(PAGE_URL)
    if not captcha_result:
        print("Captcha solving failed.")
        return

    captcha_token = captcha_result.get("token")
    print('Captcha_Result:', captcha_result)

    for proxy in working_proxies:
        use_proxy(proxy, captcha_token, encrypted_password, applicant_data)


if __name__ == "__main__":
    main()
