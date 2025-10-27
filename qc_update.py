import streamlit as st
import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

try:
    subprocess.run("apt-get update", shell=True, check=False)
    subprocess.run("apt-get install -y chromium-browser chromium-chromedriver", shell=True, check=False)
    os.environ["PATH"] += os.pathsep + "/usr/lib/chromium-browser/"
except Exception as e:
    st.warning(f"⚠️ Chrome setup failed: {e}")

st.set_page_config(page_title="AML GUI Automation", layout="centered")
st.title("AML GUI Automation Web App")

# User input section
login_url = "https://aml-gui.chargebackzero.com/index.php"
username = st.text_input("Enter Username", "")
password = st.text_input("Enter Password", "", type="password")

input_text = st.text_area("Paste IDs (one per line):")
run_btn = st.button("Run Automation")

def login_and_process_ids(login_url, username, password, ids):
    # Selenium setup
    # options = webdriver.ChromeOptions()
    # options.add_argument('--start-maximized')
    # # options.add_argument('--headless')  # Uncomment if you want headless mode

    # driver = webdriver.Chrome(options=options)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless on Streamlit
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(login_url)

    try:
        wait = WebDriverWait(driver, 15)

        username_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div/div/div/form/div[1]/input")))
        password_field = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/form/div[2]/input")
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Dropdowns
        dropdown_customer = Select(driver.find_element(By.ID, "inputcustomer"))
        dropdown_customer.select_by_visible_text("Mystery Shopping")

        dropdown_platform = Select(driver.find_element(By.ID, "inputplatform"))
        dropdown_platform.select_by_visible_text("Merchant Laundering")

        time.sleep(10)
        signin_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div/div/div/form/button")))
        signin_button.click()

        results = []
        for index, id_val in enumerate(ids):
            url = f"https://aml-gui.chargebackzero.com/update_mfilter_npci.php?id={id_val}"
            st.info(f"Processing ID {index+1} ({id_val}): {url}")
            # Open new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            try:
                element_to_click = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div/div[4]/div/button")))
                element_to_click.click()
                time.sleep(1)
                results.append((id_val, "Success"))
            except Exception as e:
                results.append((id_val, f"Failed: {e}"))
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        st.success("All IDs processed. See below for details:")
        for id_val, status in results:
            st.write(f"{id_val} — {status}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        driver.quit()

if run_btn:
    ids = [i.strip() for i in input_text.split('\n') if i.strip()]
    if username and password and ids:
        login_and_process_ids(login_url, username, password, ids)
    else:
        st.warning("Please fill in all fields and paste at least one ID.")