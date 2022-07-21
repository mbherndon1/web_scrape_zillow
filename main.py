from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import json
import os

# get around zillow captcha with header
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/103.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# retrieve zillow data
zillow_url = "https://www.zillow.com/homes/Charlotte,-NC_rb/"
response = requests.get(url=zillow_url, headers=header)
zillow_results = response.text
soup = BeautifulSoup(zillow_results, "html.parser")

# json format
script_data = soup.find('script', {'data-zrr-shared-data-key': 'mobileSearchPageStore'}).text
json_data = json.loads(script_data.split('--')[1])
json_data_cleaned = json_data["cat1"]["searchResults"]['listResults']

# get zillow links
property_links = [link['detailUrl'] for link in json_data_cleaned]
property_links_list = []
for link in property_links:
    if "https" not in link:
        complete_link = "https://zillow.com" + link
        property_links_list.append(complete_link)
    else:
        property_links_list.append(link)

# get zillow  prices
property_price_list = []
for data in json_data_cleaned:
    try:
        property_price = data['unformattedPrice']
    except KeyError:
        property_price = data['units'][0]['price']
        property_price_list.append(property_price)
    else:
        property_price_list.append(property_price)

# convert price list of strings and integers into all strings for cleaning
strings = [str(x) for x in property_price_list]
# Remove all unwanted characters
prices = [character.replace('$', '').replace('+', '').replace(',', '') for character in strings]
# Format prices
prices = ['${:0,.0f}'.format(int(price)) for price in prices]

# property address list
property_addresses = [address['address'] for address in json_data_cleaned]

# Google Form
ZILLOW_GOOGLE_FORM = os.environ['ZILLOW_GOOGLE_FORM_URL']
CHROME_DRIVER_PATH = "C:\Development\chromedriver.exe"
s = Service(CHROME_DRIVER_PATH)
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=s, options=OPTIONS)
driver.get(ZILLOW_GOOGLE_FORM)

for n in range(len(property_addresses)):
    property_address_input = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[1]/div/div/div[2]/div/"
                                                  "div[1]/div/div[1]/input")
    price_input = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[2]/div/div/div[2]/div/"
                                                "div[1]/div/div[1]/input")
    property_link_input = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/"
                                               "div[1]/div/div[1]/input")
    time.sleep(5)
    property_address_input.send_keys(property_addresses[n])
    price_input.send_keys(prices[n])
    property_link_input.send_keys(property_links_list[n])
    submit_button = driver.find_element(By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div[1]/div/span")
    submit_button.click()
    time.sleep(2)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a').click()

driver.quit()