from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

import time, mintotp, pickle

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

def login_to_forums(driver: webdriver, url: str, username: str, password: str, timeout: int, totp: bool or None = None) -> None:
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

    if totp:
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

def post_message(driver: webdriver, url: str, message: str, timeout: int) -> None:
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

def react_to_post(driver: webdriver, url: str, emote: str, timeout: int) -> None:
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