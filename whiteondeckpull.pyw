from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import os
from datetime import datetime

def log_message(message):
    log_file = r'C:\BotBrawl\automation\log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"{timestamp} - {message}\n")

def fetch_and_save_webpage_text(url, file_name):
    driver = None
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set up the WebDriver using webdriver_manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open the webpage
        driver.get(url)

        # Wait for the element with ID 'root' to be present and visible
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, 'root'))
        )

        # Extract text from the specific div
        element = driver.find_element(By.ID, 'root')
        text = element.text

        # Log and save the text to a .txt file
        log_message("Extracted Text:")
        log_message(text)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(text)
        log_message(f"Text from {url} has been saved to {file_name}")

    except Exception as e:
        error_message = f"An error occurred: {e}\n{traceback.format_exc()}"
        log_message(error_message)
    finally:
        if driver:
            driver.quit()

# Example usage
url = 'https://botbrawl.appspot.com/OnDeckWhite.html'
file_name = r'C:\BotBrawl\automation\ondeckwhite.txt'
fetch_and_save_webpage_text(url, file_name)
