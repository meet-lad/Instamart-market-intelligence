import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

import time

from instamart_engine.instamart_search_engine import (
    get_search_queue
)
from db.postgres import insert_dataframe

from datetime import datetime

#from selenium.webdriver.edge.service import Service
#from webdriver_manager.microsoft import EdgeChromiumDriverManager
#from selenium.webdriver.edge.options import Options

def refresh_instamart(driver):

    print("Refreshing Instamart...")

    try:
        driver.refresh()

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        time.sleep(3)

        return True

    except Exception as e:

        print(
            f"Refresh failed: {e}"
        )

        return False

def handle_try_again(driver):

    retry = driver.find_elements(
        By.XPATH,
        "//button[contains(., 'Retry')]"
    )

    if retry:

        print("Try Again detected.")

        retry[0].click()

        time.sleep(8)

        return True

    return False

def recover_homepage(driver):

    print("Returning to Instamart homepage...")

    return open_instamart(driver)

# ---------------------------
# Driver Setup
# ---------------------------

options = webdriver.ChromeOptions()

# Fresh Chrome profile
options.add_argument(
    "--user-data-dir=C:\\temp\\selenium_profile"
)

# Reduce automation fingerprints
options.add_argument(
    "--disable-blink-features=AutomationControlled"
)

options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation"]
)

options.add_experimental_option(
    "useAutomationExtension",
    False
)

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    ),
    options=options
)

driver.execute_script("""
Object.defineProperty(
    navigator,
    'webdriver',
    {
        get: () => undefined
    }
)
""")

# ---------------------------
# Open Instamart
# ---------------------------

def open_instamart(driver):

    target_url = "https://www.swiggy.com/instamart"

    print("Opening Instamart homepage...")

    try:
        driver.get(target_url)

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        time.sleep(3)

        retry_btn = driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="error-button"]'
        )

        if retry_btn:

            print(
                "Try Again screen on homepage."
            )

            if not refresh_instamart(driver):
                return False

        return True

    except Exception as e:

        print(
            f"Homepage open failed: {e}"
        )

        return False
    
# ---------------------------
# Set Location
# ---------------------------

def set_location(driver, area, city):

    search_text = f"{area}, {city}"

    print(
        f"Opening location popup for {search_text}"
    )

    try:
        # Open location popup
        search_boxes = driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="search-location"]'
        )

        if search_boxes:
            search_boxes[0].click()

        else:
            address_bar = WebDriverWait(
                driver,
                10
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        '[data-testid="address-bar"]'
                    )
                )
            )

            address_bar.click()

            time.sleep(2)

            search_box = WebDriverWait(
                driver,
                10
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        '[data-testid="search-location"]'
                    )
                )
            )

            search_box.click()

        time.sleep(2)

        # Location input
        location_input = WebDriverWait(
            driver,
            10
        ).until(
            EC.element_to_be_clickable(
                (
                    By.TAG_NAME,
                    "input"
                )
            )
        )

        location_input.clear()
        location_input.send_keys(
            search_text
        )

        time.sleep(3)

        # If Swiggy failed, end this attempt
        retry_btn = driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="error-button"]'
        )

        if retry_btn:

            print(
                "Try Again during location search."
            )

            return False

        # Suggestions
        results = driver.find_elements(
            By.CLASS_NAME,
            "_11n32"
        )

        print(
            f"Suggestions found: {len(results)}"
        )

        if not results:
            return False

        # First suggestion
        results[0].click()

        time.sleep(5)

        # If transition failed
        retry_btn = driver.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="error-button"]'
        )

        if retry_btn:

            print(
                "Try Again after suggestion."
            )

            return False

        # Confirm location
        buttons = driver.find_elements(
            By.TAG_NAME,
            "button"
        )

        for button in buttons:

            if "Confirm Location" in button.text:

                button.click()

                time.sleep(5)

                print(
                    f"Location set: {search_text}"
                )

                return True

        print(
            "Confirm Location not found."
        )

        return False

    except TimeoutException:

        print("Location timed out.")

        return False

    except Exception as e:

        print(
            f"Location error: {e}"
        )

        return False

# ---------------------------
# Search Keyword
# ---------------------------

def search_keyword(
        driver,
        keyword
):

    try:

        if "search" not in driver.current_url:

            search_btn = WebDriverWait(
                driver,
                30
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        '[data-testid="search-container"]'
                    )
                )
            )

            search_btn.click()

            time.sleep(5)

        search_input = WebDriverWait(
            driver,
            20
        ).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '[data-testid="search-page-header-search-bar-input"]'
                )
            )
        )

        search_input.click()

        time.sleep(2)

        search_input.clear()

        time.sleep(1)

        search_input.send_keys(
            keyword
        )
        time.sleep(5)

        search_input.send_keys(
            Keys.ENTER
        )

        time.sleep(5)

        for attempt in range(3):

            retry_btn = driver.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="error-button"]'
            )

            if not retry_btn:
                return True

            print(
                f"Try Again detected. Waiting before retry ({attempt+1}/3)"
            )

            time.sleep(5)

            retry_btn[0].click()

            time.sleep(3)

        return False

    except Exception as e:

        print(
            f"Search failed: {e}"
        )

        return False

# ---------------------------
# SKU counting in catalogue
# ---------------------------

def get_sku_count(driver, keyword):

    time.sleep(3)

    retry_btn = driver.find_elements(
        By.XPATH,
        "//button[contains(text(),'Retry')]"
    )

    if retry_btn:
        print("Retry screen detected.")
        return -1

    products = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="item-collection-card-full"]'
    )

    tokens = keyword.lower().split()

    sku_count = 0

    for product in products:

        try:
            product_name = product.find_element(
                By.CLASS_NAME,
                "_1lbNR"
            ).text

            if all(
                token in product_name.lower()
                for token in tokens
            ):
                sku_count += 1

            if sku_count >= 5:
                break

        except:
            continue

    return sku_count

#NEW RECOMMENDATION FUNCTION

def get_recommendation(sku_count):

    if sku_count == -1:
        return "Search Failed"

    elif sku_count == 0:
        return "Introduce Product"

    elif sku_count < 5:
        return "Increase Products"

    else:
        return "Sufficient Products"
    
def save_fact_sku(
        df,
        engine
):

    df.to_sql(
        "fact_sku",
        engine,
        if_exists="append",
        index=False
    )

    print(
        f"{len(df)} rows inserted."
    )
    
def get_keywords(engine):

    query = """
    SELECT
        keyword_id,
        keyword
    FROM vw_latest_keyword_state
    """

    return pd.read_sql(
        query,
        engine
    )

def save_sku_result(
        engine,
        keyword_id,
        keyword,
        city,
        area,
        sku_count
):

    recommendation = get_recommendation(
        sku_count
    )

    query = """
    INSERT INTO fact_sku
    (
        run_timestamp,
        keyword_id,
        keyword,
        city,
        area,
        sku_count,
        recommendation
    )
    VALUES
    (
        NOW(),
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    """

    with engine.raw_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            query,
            (
                keyword_id,
                keyword,
                city,
                area,
                sku_count,
                recommendation
            )
        )

        conn.commit()
# ---------------------------
# Testing
# ---------------------------

if __name__ == "__main__":

    open_instamart(driver)

    search_queue = (
        get_search_queue()
        .sort_values(
            by=[
                "city",
                "area"
            ]
        )
        .reset_index(
            drop=True
        )
        .iloc[30:46]
    )
    
    search_queue = search_queue[
        ~(
            (search_queue["city"] == "Ludhiana") &
            (search_queue["area"] == "Ghanta Ghar Chowk")
        )
    ].reset_index(drop=True)

    results = []

    current_city = None
    current_area = None

    for _, row in search_queue.iterrows():

        print(
            f"\nSearching: "
            f"{row['keyword']}"
        )

        if (
            row["city"] != current_city
            or
            row["area"] != current_area
        ):

            print(
                f"\nChanging location to "
                f"{row['area']}, "
                f"{row['city']}"
            )

            open_instamart(driver)

            location_changed = False

            for attempt in range(3):

                location_changed = set_location(
                    driver,
                    row["area"],
                    row["city"]
                )

                if location_changed:
                    break

                print(
                    f"Location attempt "
                    f"{attempt + 1}/3 failed."
                )

                # No refresh after final attempt
                if attempt < 2:

                    if not refresh_instamart(driver):
                        break

                    time.sleep(3)

            if not location_changed:

                print(
                    "Location failed after "
                    "3 attempts. Skipping."
                )

                continue

            current_city = row["city"]
            current_area = row["area"]

            time.sleep(5)

        search_success = search_keyword(
            driver,
            row["keyword"]
        )

        if not search_success:

            print(
                "Search failed. Reopening Instamart and retrying..."
            )

            open_instamart(driver)

            location_changed = set_location(
                driver,
                row["area"],
                row["city"]
            )

            if not location_changed:

                print(
                    "Location recovery failed. Skipping keyword."
                )

                continue

            current_city = row["city"]
            current_area = row["area"]
            

            time.sleep(3)

            search_success = search_keyword(
                driver,
                row["keyword"]
            )

            if not search_success:

                print(
                    "Keyword failed twice. Skipping."
                )

                continue

        sku_count = get_sku_count(
            driver,
            row["keyword"]
        )

        recommendation = (
            get_recommendation(
                sku_count
            )
        )

        print(
            "SKU Count:",
            sku_count
        )

        print(
            "Recommendation:",
            recommendation
        )

        results.append({

            "keyword_id":
                row["keyword_id"],

            "keyword":
                row["keyword"],

            "states":
                row["states"],

            "city":
                row["city"],

            "area":
                row["area"],

            "instamart_stores":
                row["instamart_stores"],

            "sku_count":
                sku_count,

            "recommendation":
                recommendation
        })

        recover_homepage(driver)

        time.sleep(5)

    fact_sku_df = pd.DataFrame(
        results
    )

    print("\nFinal Output:")
    print(fact_sku_df)

    fact_sku_df["run_timestamp"] = (
        datetime.now()
    )

    insert_dataframe(
        fact_sku_df,
        "fact_sku"
    )

    input(
        "\nPress Enter to close..."
    )

    driver.quit()