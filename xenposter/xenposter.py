from selenium import webdriver
from utils import *

import argparse

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

# Create a driver for the browser
if args.chrome and not args.remote:
    options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
    options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Excluding enable-logging Switch
    options.add_argument("disable-popup-blocking")
    options.add_argument("disable-notifications")
    options.add_argument("disable-gpu")
    driver = create_driver_for_chrome_firefox("chrome", options)
elif args.firefox and not args.remote:
    driver = create_driver_for_chrome_firefox("firefox", None)
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

if not args.login and not args.post and not args.react:
    print("This script requires you to specify what actions you want to do. Currently, --login, --post, --react are supported.")
    exit()

if args.emote not in LIST_OF_EMOTES:
    print("Invalid emote. Valid emotes are: " + ", ".join(LIST_OF_EMOTES))
    exit()

try:
    if args.login:
        login_to_forums(driver, args.url, args.username, args.password, args.timeout, args.totp)
        exit()
    if args.post:
        login_to_forums(driver, args.url, args.username, args.password, args.timeout, args.totp)
        post_message(driver, args.url, args.message, args.timeout)
        exit()
    if args.react:
        login_to_forums(driver, args.url, args.username, args.password, args.timeout, args.totp)
        react_to_post(driver, args.url, args.emote, args.timeout)
        exit()
except Exception as e:
    print(e)
    exit()
