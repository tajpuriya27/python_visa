import requests
from requests.auth import HTTPProxyAuth
import logging

# Enable verbose logging for debugging
logging.basicConfig(level=logging.DEBUG)

PROXY_TEST_URL = "https://visa.vfsglobal.com/cpv/en/prt/login"  # Replace with the URL you want to test against

def check_proxy(proxy):
    """
    Check if a given proxy is working.

    Args:
    - proxy (str): The proxy string in the format "ip:port:user:password".

    Returns:
    - dict: A dictionary containing proxy status and response or error message.
    """
    try:
        ip, port, user, password = proxy.split(':')
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        
        # Use HTTPProxyAuth for proxy authentication
        proxy_auth = HTTPProxyAuth(user, password)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        # Make the request
        response = requests.get(PROXY_TEST_URL, proxies=proxies, headers=headers, auth=proxy_auth, timeout=10, verify=False)
        
        # Return the result based on status code
        if response.status_code == 200:
            return {"proxy": proxy, "status": "working", "response": response.text}
        else:
            return {"proxy": proxy, "status": "failed", "error": f"Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"proxy": proxy, "status": "failed", "error": str(e)}
    except ValueError:
        return {"proxy": proxy, "status": "failed", "error": "Invalid proxy format"}

def active_proxies(proxies_list):
    """
    Check all proxies from the list and return the working ones.

    Args:
    - proxies_list (list): A list of proxy strings.

    Returns:
    - list: A list of working proxy strings.
    """
    working_proxies = []
    for proxy in proxies_list:
        result = check_proxy(proxy)
        if result["status"] == "working":
            print(f"Proxy {proxy} is working.")
            working_proxies.append(proxy)
        else:
            print(f"Proxy {proxy} failed. Reason: {result['error']}")
    return working_proxies

if __name__ == "__main__":
    with open('proxies.txt', 'r') as file:
        proxies_list = [line.strip() for line in file.readlines()]

    working_proxies = active_proxies(proxies_list)
    print("Working proxies:", working_proxies)
