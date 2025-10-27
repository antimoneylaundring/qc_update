# import streamlit as st
# import time
# import os
# import subprocess
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service

# try:
#     subprocess.run("apt-get update", shell=True, check=False)
#     subprocess.run("apt-get install -y chromium-browser chromium-chromedriver", shell=True, check=False)
#     os.environ["PATH"] += os.pathsep + "/usr/lib/chromium-browser/"
# except Exception as e:
#     st.warning(f"⚠️ Chrome setup failed: {e}")

# st.set_page_config(page_title="AML GUI Automation", layout="centered")
# st.title("AML GUI Automation Web App")

# # User input section
# login_url = "https://aml-gui.chargebackzero.com/index.php"
# username = st.text_input("Enter Username", "")
# password = st.text_input("Enter Password", "", type="password")

# input_text = st.text_area("Paste IDs (one per line):")
# run_btn = st.button("Run Automation")

# def login_and_process_ids(login_url, username, password, ids):
#     # Selenium setup
#     # options = webdriver.ChromeOptions()
#     # options.add_argument('--start-maximized')
#     # # options.add_argument('--headless')  # Uncomment if you want headless mode

#     # driver = webdriver.Chrome(options=options)
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--headless")  # Run headless on Streamlit
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--disable-software-rasterizer")

#     service = Service("/usr/bin/chromedriver")
#     driver = webdriver.Chrome(service=service, options=chrome_options)

#     driver.get(login_url)

#     try:
#         wait = WebDriverWait(driver, 15)

#         username_field = wait.until(EC.presence_of_element_located(
#             (By.XPATH, "/html/body/div[1]/div/div/div/div/form/div[1]/input")))
#         password_field = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/form/div[2]/input")
#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         # Dropdowns
#         dropdown_customer = Select(driver.find_element(By.ID, "inputcustomer"))
#         dropdown_customer.select_by_visible_text("Mystery Shopping")

#         dropdown_platform = Select(driver.find_element(By.ID, "inputplatform"))
#         dropdown_platform.select_by_visible_text("Merchant Laundering")

#         time.sleep(10)
#         signin_button = wait.until(EC.element_to_be_clickable(
#             (By.XPATH, "/html/body/div[1]/div/div/div/div/form/button")))
#         signin_button.click()

#         results = []
#         for index, id_val in enumerate(ids):
#             url = f"https://aml-gui.chargebackzero.com/update_mfilter_npci.php?id={id_val}"
#             st.info(f"Processing ID {index+1} ({id_val}): {url}")
#             # Open new tab
#             driver.execute_script("window.open('');")
#             driver.switch_to.window(driver.window_handles[-1])
#             driver.get(url)
#             try:
#                 element_to_click = WebDriverWait(driver, 30).until(
#                     EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div/div[4]/div/button")))
#                 element_to_click.click()
#                 time.sleep(1)
#                 results.append((id_val, "Success"))
#             except Exception as e:
#                 results.append((id_val, f"Failed: {e}"))
#             driver.close()
#             driver.switch_to.window(driver.window_handles[0])

#         st.success("All IDs processed. See below for details:")
#         for id_val, status in results:
#             st.write(f"{id_val} — {status}")

#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#     finally:
#         driver.quit()

# if run_btn:
#     ids = [i.strip() for i in input_text.split('\n') if i.strip()]
#     if username and password and ids:
#         login_and_process_ids(login_url, username, password, ids)
#     else:
#         st.warning("Please fill in all fields and paste at least one ID.")


import streamlit as st
import time
import os
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="AML GUI Automation", layout="centered")
st.title("AML GUI Automation Web App")

login_url = "https://aml-gui.chargebackzero.com/index.php"
username = st.text_input("Enter Username", "")
password = st.text_input("Enter Password", "", type="password")
run_btn = st.button("Run Automation")

COOKIE_FILE = "cookies.pkl"

def save_cookies(driver):
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver):
    with open(COOKIE_FILE, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)

def get_chrome_driver(headless=True):
    chrome_options = webdriver.ChromeOptions()
    if not headless:
        st.info("Opening Chrome (visible) to solve captcha...")
        chrome_options.add_argument("--start-maximized")
    else:
        st.info("Running headless (no window)...")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def run_automation():
    # Check if cookies exist
    first_time = not os.path.exists(COOKIE_FILE)

    driver = get_chrome_driver(headless=not first_time)
    driver.get(login_url)

    if first_time:
        st.warning("Please solve the captcha manually in the Chrome window.")
        wait = WebDriverWait(driver, 300)  # wait up to 5 min for manual login
        try:
            # Wait until user logs in manually (detect by new element on dashboard)
            wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
            save_cookies(driver)
            st.success("Captcha solved and cookies saved! You can close Chrome now.")
        except Exception as e:
            st.error(f"Timeout or error: {e}")
            driver.quit()
            return
    else:
        # Load cookies and skip login
        driver.get(login_url)
        load_cookies(driver)
        driver.refresh()
        st.success("Logged in using saved cookies (no captcha).")

    # Continue automation after login
    # Example: Navigate to some page
    driver.get("https://aml-gui.chargebackzero.com/dashboard.php")
    st.write("Automation running...")

    # Your logic continues here...

    driver.quit()

if run_btn:
    if username and password:
        run_automation()
    else:
        st.warning("Please fill in username and password.")
