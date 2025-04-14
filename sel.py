from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

def clone_page(target_url, output_folder="clones", filename="index.html"):
    # Setup headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(target_url)
        time.sleep(5)  # wait for JS to load

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        filepath = os.path.join(output_folder, filename)

        # Save page source
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print(f"[+] Cloned {target_url} saved to {filepath}")
        return filepath

    except Exception as e:
        print(f"[!] Error cloning page: {e}")
        return None

    finally:
        driver.quit()
