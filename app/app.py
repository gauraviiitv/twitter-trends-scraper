import os
import time
import uuid
import requests
from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Import TimeoutException
from pymongo import MongoClient, errors
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def get_ip_address():
    try:
        ip = requests.get('https://api.ipify.org').text
        return ip
    except requests.RequestException:
        return "N/A"
    
def get_driver_with_proxy():
    # Set Chrome options
    chrome_options = Options()
    # proxy = os.getenv("PROXY")
    # chrome_options.proxy = Proxy({ 'proxyType': ProxyType.MANUAL, 'httpProxy' : proxy, 'httpsProxy' : proxy})
    chrome_options.add_argument("--window-size=1400,600")
    chrome_options.add_argument("--headless")  # Headless mode for Docker
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")


    try:
        # Initialize the WebDriver using the prebuilt image's path
        service = Service("/usr/bin/chromedriver")  # Path to ChromeDriver in the container
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver successfully initialized.")
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None


def scrape_twitter_trends():
    driver = get_driver_with_proxy()
    if not driver:
        print("Failed to initialize the WebDriver. Exiting.")
        return {'error': 'WebDriver initialization failed'}

    try:
        driver.get("https://x.com/i/flow/login")

        username = os.getenv("TWITTER_USERNAME")
        password = os.getenv("TWITTER_PASSWORD")
        phone = os.getenv("TWITTER_PHONE")  # Phone or email for verification

        if not username or not password:
            print("Twitter credentials not found. Exiting.")
            driver.quit()
            return

        wait = WebDriverWait(driver, 10)  
        # Wait for username field to appear
        try:
            # Wait for the page to load completely
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # Locate the username field
            username_field = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="text" and @autocomplete="username"]'))
            )
            username_field.send_keys(username)
            print("Username entered successfully.")
        except TimeoutException:
            print("Username field not found. Check the selector or page structure.")
            driver.quit()

        # Click "Next" button
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]')))
        next_button.click()
        print("Next button clicked.")
        
        try:
            # Wait for the page to load completely
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # Locate the username field
            username_field = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="text"]'))
            )
            username_field.send_keys(phone)
            print("Phone entered successfully.")
        except TimeoutException:
            print("Phone field not found. Check the selector or page structure.")
            driver.quit()

        # Click "Next" button
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]')))
        next_button.click()
        print("Next button clicked.")

        # Wait for password field and enter it
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            password_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
            password_field.send_keys(password)
            print("Password entered successfully.")
        except TimeoutException:
            print("Password field not found. Exiting.")
            driver.quit()


        # Click "Log in" button
        try:
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]')))
            login_button.click()
            print("Login button clicked.")
        except TimeoutException:
            print("Login button not clickable. Exiting.")
            driver.quit()
        print("Login successful.")

        # Wait for the trending section to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Trending now']")))
        print("Trending section loaded successfully.")

        # Scrape trends
        trends = driver.find_elements(By.XPATH, "//div[@aria-label='Timeline: Trending now']//div[contains(@class, 'css-175oi2r')]//span")
        trends_list = [trend.text for trend in trends if trend.text.strip()]
        print("Trends scraped successfully.")
        # Substrings to filter out
        filter_substrings = ["post", "trend", "happening", "Politics", "Sports", "Live", "Show more", "\u00b7"]
        print("Trends before filtering: ", trends_list)
        # Remove elements that contain any of the substrings
        trends_list = list({
            s.lower(): s for s in trends_list  # Use a dict to keep the original casing but remove case-insensitive duplicates
            if not any(substring.lower() in s.lower() for substring in filter_substrings)}.values())
        print("Trends filtered successfully.")
        print(trends_list)

        unique_id = str(uuid.uuid4())
        ip_address = get_ip_address()  # Fetch from API if needed

        store_to_mongodb(unique_id, trends_list, ip_address)

    except Exception as e:
        print(f"Error during scraping: {e}")
        return {'error': str(e)}
    finally:
        driver.quit()
    return unique_id, trends_list, ip_address

def store_to_mongodb(unique_id, trends, ip_address):
    uri = os.getenv("MONGODB_URI")
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client['twitter_trends_db']
        collection = db['trends']

        record = {
            "unique_id": unique_id,
            "trends": trends,
            "date_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": ip_address
        }

        collection.insert_one(record)
        return record
    except errors.ConnectionError as e:
        print(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        print(f"Error storing data to MongoDB: {e}")
        return None

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    result = scrape_twitter_trends()
    if result:
        return jsonify(result)
    return jsonify({'error': 'Failed to run script'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
