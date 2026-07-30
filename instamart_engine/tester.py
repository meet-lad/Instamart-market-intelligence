from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()

options.add_argument("--user-data-dir=C:\\temp\\selenium_profile")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    ),
    options=options
)

driver.get("https://www.swiggy.com/instamart")

input("Observe the page and press Enter...")

driver.quit()