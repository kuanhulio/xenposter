from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

import argparse, time, os, mintotp, pickle

# Create a parser for the command line arguments
parser = argparse.ArgumentParser(description='xenposter - XenForo Automation Script')

required = parser.add_argument_group('required arguments')
required.add_argument('url', help='The URL of the XenForo forum thread')
required.add_argument('-u', '--username', help='Username', required=True)
required.add_argument('-p', '--password', help='Password', required=True)

xenforo_action = parser.add_argument_group('xenforo actions')
xenforo_action.add_argument('-l', '--login', help='Login to XenForo and do nothing', action='store_true')
xenforo_action.add_argument('--post', help='Post a message to the XenForo thread', action='store_true')
xenforo_action.add_argument('--react', help='React to a post in the XenForo thread', default="like")

browser_options = parser.add_argument_group('browser options')
browser_options.add_argument('-c', '--chrome', action='store_true', help='Use Chrome')
browser_options.add_argument('-f', '--firefox', action='store_true', help='Use Firefox')
browser_options.add_argument('-r', '--remote', action='store_true', help='Use remote driver')

optional = parser.add_argument_group('optional arguments')
optional.add_argument('-t', '--totp', help="TOTP Secret Key, required if you've set up 2FA")
optional.add_argument('--timeout', type=int, default=1, help='Timeout for the browser')
optional.add_argument('-e', '--emote', help='Emote to use', default="like")

remote_options = parser.add_argument_group('remote options')
remote_options.add_argument("--remote-site", help="Remote site to use")
remote_options.add_argument("--remote-port", help="Remote port to use")

args = parser.parse_args()

LIST_OF_EMOTES = [
    "like",
    "love",
    "haha",
    "wow",
    "sad",
    "angry",
    "dislike",
    "turdle"
]

def save_cookie(driver: webdriver.Chrome or webdriver.Firefox or webdriver.Remote, path: str) -> None:
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver: webdriver.Chrome or webdriver.Firefox or webdriver.Remote, path: str) -> None:
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie) 

def create_driver_for_chrome_firefox(browser_choice: str, options: webdriver.ChromeOptions or webdriver.FirefoxOptions or None) -> webdriver.Chrome or webdriver.Firefox or Exception:
    if browser_choice == "chrome":
        if options is None:
            options = webdriver.ChromeOptions()
        return webdriver.Chrome(options=options)
    elif browser_choice == "firefox":
        if options is None:
            options = webdriver.FirefoxOptions()
        return webdriver.Firefox(options=options)
    else:
        raise Exception("No browser specified")

def create_driver_for_remote(browser_choice: str, options: webdriver.ChromeOptions or webdriver.FirefoxOptions or None, remote_site: str, remote_port: str) -> webdriver.Remote or Exception:
    if browser_choice == "chrome":
        if options is None:
            options = webdriver.ChromeOptions()
        return webdriver.Remote(
            command_executor=f"http://{remote_site}:{remote_port}",
            options=options
        )
    elif browser_choice == "firefox":
        if options is None:
            options = webdriver.FirefoxOptions()
        return webdriver.Remote(
            command_executor=f"http://{remote_site}:{remote_port}",
            options=options
        )
    else:
        raise Exception("No browser specified")

# Create a driver for the browser
if args.chrome and not args.remote:
    options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
    options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Excluding enable-logging Switch
    options.add_argument("disable-popup-blocking")
    options.add_argument("disable-notifications")
    options.add_argument("disable-gpu")
    driver = create_driver_for_chrome_firefox("chrome", options, None, None)
elif args.firefox and not args.remote:
    driver = create_driver_for_chrome_firefox("firefox", None, None, None)
elif args.remote:
    if args.chrome:
        options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
        options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Excluding enable-logging Switch
        options.add_argument("disable-popup-blocking")
        options.add_argument("disable-notifications")
        options.add_argument("disable-gpu")
        driver = create_driver_for_remote(
            "chrome",
            options,
            args.remote_site,
            args.remote_port
        )
    elif args.firefox:
        driver = create_driver_for_remote(
            "firefox",
            None,
            args.remote_site,
            args.remote_port
        )
else:
    print("This script requires a browser to be specified. Use -c for Chrome or -f for Firefox.")
    exit()

if not args.login or not args.post or not args.react:
    print("This script requires you to specify what actions you want to do. Currently, --login, --post, --react are supported.")
    exit()

if args.emote not in LIST_OF_EMOTES:
    print("Invalid emote. Valid emotes are: " + ", ".join(LIST_OF_EMOTES))
    exit()

def login_to_forums(url: str, username: str, password: str, timeout: int, totp: bool or None = None) -> None:
    url_parsed = urlparse(url)
    driver.get(f"{url_parsed.scheme}://{url_parsed.netloc}/login")
    time.sleep(timeout)

    # Accept Cookies
    try: 
        elem = driver.find_element(By.CLASS_NAME, "js-noticeDismiss.button--notice.button.button--icon.button--icon--confirm")
        elem.click()
    except Exception as e:
        print("No notice found")

    # Find the username and password fields
    username_field = driver.find_element(By.NAME, "login")
    password_field = driver.find_element(By.NAME, "password")

    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Press the login button
    time.sleep(timeout)
    password_field.send_keys(Keys.RETURN)

    if args.totp:
        # Generate a TOTP code
        totp_code = mintotp.totp(totp)
        # Enter the TOTP code
        elem = driver.find_element(By.NAME, "code")
        elem.send_keys(totp_code)
        # Click the submit button
        elem = driver.find_element(By.CLASS_NAME, "button--primary.button.button--icon.button--icon--login")
        time.sleep(timeout)
        elem.click()
    
    time.sleep(timeout)

    # Save the cookies
    save_cookie(driver, "cookies.pkl")

def post_message(url: str, message: str, timeout: int) -> None:
    # Load the cookies
    load_cookie(driver, "cookies.pkl")

    # Go to the thread
    driver.get(url)
    time.sleep(timeout)

    # Find the message field
    message_box = driver.find_element(By.CLASS_NAME, "fr-element.fr-view")

    # Enter the message
    message_box.send_keys(message)

    # Press the post button
    message_box.send_keys(Keys.CONTROL, Keys.RETURN)

def react_to_post(url: str, emote: str, timeout: int) -> None:
    # Load the cookies
    load_cookie(driver, "cookies.pkl")

    # Go to the thread
    for index, emote_from_list in enumerate(LIST_OF_EMOTES):
        if emote_from_list == emote:
            driver.get(f"{url}/react?reaction_id={index}")
        
    time.sleep(timeout)

    # Find the react confirm button
    react_confirm_button = driver.find_element(By.CLASS_NAME, "button--primary.button.button--icon.button--icon--confirm")

    # Click the react confirm button
    react_confirm_button.click()

try:
    if args.login:
        login_to_forums(args.url, args.username, args.password, args.timeout, args.totp)
    if args.post:
        login_to_forums(args.url, args.username, args.password, args.timeout, args.totp)
        post_message(args.url, args.message, args.timeout)
    if args.react:
        login_to_forums(args.url, args.username, args.password, args.timeout, args.totp)
        react_to_post(args.url, args.emote, args.timeout)
except Exception as e:
    print(e)
    exit()
