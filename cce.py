import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import requests as http_requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service_instance = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service_instance, options=chrome_options)
    return driver

def send_pushover_notification(message, user_key, api_token):
    logging.info(f"Sending notification: {message}")
    r = http_requests.post("https://api.pushover.net/1/messages.json", data={
        "token": api_token,
        "user": user_key,
        "message": message
    })
    if r.status_code == 200:
        logging.info("Notification sent successfully.")
    else:
        logging.error(f"Failed to send notification. Status code: {r.status_code}")

def check_availability():
    driver = get_driver()
    logging.info("Driver initialized in headless mode.")
    driver.get("https://ujop.cuni.cz/UJOP-371.html?ujopcmsid=8:zkouska-z-ralii-a-cestiny-pro-obcanstvi-cr")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "select_misto_zkousky")))

    USER_KEY = 'your_user_key'
    API_TOKEN = 'your_api_token'
    target_places = ["Praha-Krystal", "Praha-Voršilská", "Poděbrady"]
    exam_type = 'pouze český jazyk'
    dates = ["25.05.2024", "14.06.2024"]

    place_select = Select(driver.find_element(By.ID, "select_misto_zkousky"))

    # Open a log file to write the outputs
    with open("available_seats_summary.txt", "a") as log_file:
        for index in range(1, len(place_select.options)):
            place = place_select.options[index].text
            if place in target_places:
                place_select.select_by_index(index)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select_cast_zkousky")))
                Select(driver.find_element(By.ID, "select_cast_zkousky")).select_by_visible_text(exam_type)
                time.sleep(1)
                date_select = Select(driver.find_element(By.ID, "select_termin"))

                for date_to_find in dates:
                    date_options = [option.text for option in date_select.options]
                    if date_to_find in date_options:
                        date_select.select_by_visible_text(date_to_find)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "qxid")))
                        available_seats = driver.find_element(By.ID, "qxid").text
                        if available_seats.isdigit() and int(available_seats) > 1:
                            message = f"Available seats for {place}: {available_seats} for exam type: {exam_type} on {date_to_find}"
                            print(message)
                            log_file.write(message + "\n")
                            send_pushover_notification(message, USER_KEY, API_TOKEN)
                            log_message = f"{datetime.datetime.now()}: {message}"
                            log_file.write(log_message + "\n")
                        else:
                            message = f"No available seats for {place} for exam type: {exam_type} on {date_to_find}"
                            print(message)
                            log_message = f"{datetime.datetime.now()}: {message}"
                            log_file.write(log_message + "\n")
                    else:
                        message = f"Date {date_to_find} not available for {place} for exam type: {exam_type}"
                        print(message)
                        log_message = f"{datetime.datetime.now()}: {message}"
                        log_file.write(log_message + "\n")

    driver.quit()
    logging.info("Driver session ended.")

if __name__ == '__main__':
    check_availability()
