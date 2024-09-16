Open this website and create new account with your gmail and edit email and password in the .env file.
https://visa.vfsglobal.com/cpv/en/prt/login

If the website says wait 2 hours or does not work use proxy from proxy list text then login.

Capsolver file used to solve cloudflare turnstile captcha and returns token.

Encryption file used to encrypt password with RSA encryption.

Proxy file is used to test if the proxy is working or not by checking from Httpbin site.

First run vfs_api_1 , the 200 response sends OTP in your gmail note that.

Then, run vfs_api_2, it will ask OTP as input.[ OTP can be used while running this code until you generate new OTP code or 5 minutes valid. Generating 10 OTP code blocks the account for 24 hours then you need new account.] Login response 200 gives accessToken which is used to update headers and make further requests.

Response cookies are updated and using same session application and checkslot api are called with required json payload.

You can verify payload from the browser and for headers only required headers are passed as other can be ignored and does not effect in making requests.

Don't forget to install requirements before you run the code !!

Also if you are getting 403 error (proxy not working) then run again code or uncomment another proxy in proxy list at start of code until you get 200 !!!

#### BEST OF LUCK
