import os
import time
import getpass
import datetime
from selenium import webdriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from random import uniform
from json import load, dump

def typeThere(un, where):
    for k in un:
        where.send_keys(k)
        time.sleep(uniform(0.2, 0.5))
    time.sleep(uniform(2, 3))

def eraseThere(un, where):
    for _ in range(len(un)):
        where.send_keys(Keys.BACKSPACE)
    time.sleep(uniform(2, 3))

def findExact(driver, mouse, un):
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{un}']")))
    driver.execute_script("arguments[0].scrollIntoView();", element)
    mouse.move_to_element(element).click().perform()
    time.sleep(uniform(2, 4))

def input_account_info():
    USERNAME = input("Username: ")
    PASSWORD = getpass.getpass("Password: ")
    return USERNAME, PASSWORD

def input_2fa_code():
    CODE = input("2FA Code: ")
    return CODE

def login_instagram(driver, USERNAME, PASSWORD):
    driver.get("https://www.instagram.com/")
    username = WebDriverWait(driver, 30).until(
        EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
    )
    password = WebDriverWait(driver, 30).until(
        EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='pass']"))
        )
    )
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    password.send_keys(Keys.RETURN)

def complete_2fa(driver):
    code = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='verificationCode']")))
    CODE = input_2fa_code()
    code.send_keys(CODE)
    code.send_keys(Keys.RETURN)

def load_cookies():
    if not os.path.exists("cookies.json"):
        return None
    with open("cookies.json", "r") as f:
        cookies = load(f)
    return cookies

def save_cookies(driver):
    with open("cookies.json", "w") as f:
        dump(driver.get_cookies(), f)

def go_to_profile(driver, USERNAME):
    driver.get(f"https://www.instagram.com/{USERNAME}/")
    time.sleep(5)

def go_to_closed_friends(driver):
    driver.get("https://www.instagram.com/accounts/close_friends/")
    time.sleep(5)

def get_followers_count(driver, USERNAME):
    if driver.current_url != f"https://www.instagram.com/{USERNAME}/":
        go_to_profile(driver, USERNAME)
    fcount = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, f"//a[@href='/{USERNAME}/followers/']/span/span/span"))).text)
    return fcount

def get_followers_list(driver, fcount):
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, f"//a[@href='/{USERNAME}/followers/']"))).click()
    time.sleep(5)

    scrolldiv = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]')))
    scount = 0
    while fcount > scount:
        for x in range(1000):
            scrolldiv.send_keys(Keys.ARROW_DOWN)
        felements = driver.find_elements(By.XPATH, '/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div/div[1]')
        scount = len(felements)

    followers = [follower.text for follower in felements]
    return followers, felements

def save_followers(USERNAME, followers):
    os.makedirs(f"{datetime.date.today()}/{USERNAME}", exist_ok=True)
    with open(f"{datetime.date.today()}/{USERNAME}/followers.txt", "w") as f:
        f.write("\n".join(followers))

def add_users_to_close_friends(driver, mouse, followers):
    go_to_closed_friends(driver)
    search_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']")))
    index = 0
    failed = []
    for uname in followers:
        try:
            typeThere(uname, search_section)
            time.sleep(uniform(2, 4))
            findExact(driver, mouse, uname)
            time.sleep(uniform(2, 4))
        except:
            print(f"Couldn't add {uname}")
            failed.append(uname)
        eraseThere(uname, search_section)
        time.sleep(uniform(2, 4))
        print(f'Added [{index}/{len(followers)}] to close friends')
        index += 1
    return failed


driver = uc.Chrome()
driver.maximize_window()
mouse = ActionChains(driver)

USERNAME, PASSWORD = input_account_info()
cookies = load_cookies()
if cookies:
    driver.get("https://www.instagram.com/")
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    driver.refresh()
    print("Logged in using cookies")
    time.sleep(5)
else:
    print("no cookies found, logging in manually")

    login_instagram(driver, USERNAME, PASSWORD)
    
    there_is_2fa = input("Is there 2FA (y/n)? ").lower() == 'y'

    if there_is_2fa:
        complete_2fa(driver)
    
    save_cookies(driver)
    print("Logged in manually")

os.makedirs(f"{datetime.date.today()}/{USERNAME}", exist_ok=True)
time.sleep(5)
print("Logged in")

time.sleep(uniform(10, 15)) 

# driver.get(f"https://www.instagram.com/{USERNAME}/")

# fcount = get_followers_count(driver, USERNAME)
# print(f'You have {fcount} followers')

# followers, felements = get_followers_list(driver, fcount)
# print(f'You\'ve collected {len(followers)} usernames')

# save_followers(USERNAME, followers)

# go_to_closed_friends(driver)

# failed = add_users_to_close_friends(driver, mouse, followers)

# print("Done!")

# if failed:
#     print(f'Failed to add {len(failed)} followers')
#     with open(f"{datetime.date.today()}/{USERNAME}/failed.txt", "w") as f:
#         f.write("\n".join(failed))
# else:
#     print("All followers added")

driver.quit()
