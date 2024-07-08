from selenium.webdriver import Chrome, ChromeOptions, ChromeService, Keys
from selenium.webdriver.common.by import By
import json, os, asyncio, platform


# From: https://medium.com/@ghulammustafapy/efficient-login-session-management-in-selenium-python-save-and-reuse-credentials-for-browser-7aa21b32df63
def saveCookies(driver):
    # Get and store cookies after login
    cookies = driver.get_cookies()

    # Store cookies in a file
    with open("json/cookies.json", "w") as file:
        json.dump(cookies, file)
    print("New Cookies saved successfully")


def loadCookies(driver):
    # Check if cookies file exists
    if "cookies.json" in os.listdir("json"):
        # Load cookies to a vaiable from a file
        with open("json/cookies.json", "r") as file:
            cookies = json.load(file)

        # Set stored cookies to maintain the session
        for cookie in cookies:
            driver.add_cookie(cookie)
    else:
        print("No cookies file found")

    driver.refresh()  # Refresh Browser after login


async def launch_driver():
    options = ChromeOptions()
    # With Chrome UI (for testing)
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("detach", True)
    # Without Chrome UI (for production, not working for raspberry pi)
    # options.add_argument("--headless=new")

    if platform.node() == "raspberrypi":
        service = ChromeService(
            executable_path="/usr/lib/chromium-browser/chromedriver"
        )
        driver = Chrome(options=options, service=service)
    else:
        driver = Chrome(options=options)
    await asyncio.sleep(1)
    # driver.minimize_window()

    driver.get("https://missionchief.co.uk/users/sign_in")
    await asyncio.sleep(1)
    loadCookies(driver)
    await asyncio.sleep(1)

    if "sign_in" in driver.current_url:
        # Login process
        driver.find_element(By.CSS_SELECTOR, "#user_email").send_keys(
            os.getenv("MC_USERNAME")
        )
        driver.find_element(By.CSS_SELECTOR, "#user_password").send_keys(
            os.getenv("MC_PASSWORD")
        )
        remember_me = driver.find_element(By.CSS_SELECTOR, "#user_remember_me")
        remember_me.click()
        remember_me.send_keys(Keys.RETURN)
        await asyncio.sleep(5)

        # After successful login save new session cookies ot json file
        saveCookies(driver)
    else:
        print("Previous session loaded")

    return driver
