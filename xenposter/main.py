from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import argparse
import time
import os
import mintotp
import pickle

# Create a parser for the command line arguments
parser = argparse.ArgumentParser(description='Automatically post to XenForo')

required = parser.add_argument_group('required arguments')
required.add_argument('url', help='The URL of the XenForo forum thread')
required.add_argument('-u', '--username', help='Username', required=True)
required.add_argument('-p', '--password', help='Password', required=True)
required.add_argument('-m', '--message', help='Message', required=True)

browser_options = parser.add_argument_group('browser options')
browser_options.add_argument('-c', '--chrome', action='store_true', help='Use Chrome')
browser_options.add_argument('-f', '--firefox', action='store_true', help='Use Firefox')
browser_options.add_argument('-r', '--remote', action='store_true', help='Use remote driver')

optional = parser.add_argument_group('optional arguments')
optional.add_argument('-t', '--totp', help="TOTP Secret Key, required if you've set up 2FA")
optional.add_argument('--timeout', type=int, default=1, help='Timeout for the browser')

remote_options = parser.add_argument_group('remote options')
remote_options.add_argument("--remote-site", help="Remote site to use")
remote_options.add_argument("--remote-port", help="Remote port to use")

args = parser.parse_args()

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver, path):
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie) 

# Create a driver for the browser
if args.chrome and not args.remote:
    options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
    options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Excluding enable-logging Switch
    options.add_argument("disable-popup-blocking")
    options.add_argument("disable-notifications")
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome(options=options, service_log_path=os.devnull)
elif args.firefox and not args.remote:
    driver = webdriver.Firefox(log_path=os.devnull)
elif args.remote:
    if args.chrome:
        options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
        options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Excluding enable-logging Switch
        options.add_argument("disable-popup-blocking")
        options.add_argument("disable-notifications")
        options.add_argument("disable-gpu")
        driver = webdriver.Remote(
            command_executor=f"{args.remote_site}:{args.remote_port}",
            options=options
        )
    elif args.firefox:
        driver = webdriver.Remote(
            command_executor=f"{args.remote_site}:{args.remote_port}",
            options=webdriver.FirefoxOptions()
        )
else:
    # driver = webdriver.Remote()
    print("This script requires a browser to be specified. Use -c for Chrome or -f for Firefox.")
    exit()

def first_step():
    # Load the page
    driver.get("https://edgegamers.com/login")
    time.sleep(args.timeout)

    try: 
        elem = driver.find_element(By.CLASS_NAME, "js-noticeDismiss.button--notice.button.button--icon.button--icon--confirm")
        elem.click()
    except Exception as e:
        print("No notice found")

    # Find the username and password fields
    username = driver.find_element(By.NAME, "login")
    password = driver.find_element(By.NAME, "password")

    # Enter the username and password
    username.send_keys(args.username)
    password.send_keys(args.password)

    # Press the login button
    time.sleep(args.timeout)
    password.send_keys(Keys.RETURN)

    if args.totp:
        # Generate a TOTP code
        totp = mintotp.totp(args.totp)
        # Enter the TOTP code
        elem = driver.find_element(By.NAME, "code")
        elem.send_keys(totp)
        # Click the submit button
        elem = driver.find_element(By.CLASS_NAME, "button--primary.button.button--icon.button--icon--login")
        time.sleep(args.timeout)
        elem.click()
    
    time.sleep(args.timeout)

def second_step():
    # Load the page
    driver.get(args.url)
    load_cookie(driver, "cookies.pkl")
    time.sleep(args.timeout)

    # Find the message field
    message_box = driver.find_element(By.CLASS_NAME, "fr-element.fr-view")

    # Enter the message
    message_box.send_keys(args.message)

    # Press the post button
    message_box.send_keys(Keys.CONTROL, Keys.RETURN)

try:
    first_step()
    second_step()
except Exception as e:
    print(f"Error: {e}")
    exit()
