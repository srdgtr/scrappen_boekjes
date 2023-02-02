# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    import selenium
except ModuleNotFoundError as ve:
    print(f"{ve} trying to install")
    install("selenium")
    import selenium

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ModuleNotFoundError as ve:
    print(f"{ve} trying to install")
    install("webdriver-manager")
    from webdriver_manager.chrome import ChromeDriverManager

# import dropbox
import img2pdf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests

date_now = datetime.now().strftime("%c").replace(":", "-")

def browser_chrome():
    options = Options()
    options.add_argument("start-maximized")
    prefs = {"profile.default_content_settings": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

driver = browser_chrome()
actions = ActionChains(driver)

delay = 20

def login():
    driver.get("https://v2.moo.nl/portal/")
    login_as_personeel = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="group-list-container"]/li[1]/div')))
    login_as_personeel.click()
    username = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userNameInput"]')))
    username.send_keys("")
    password = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordInput"]')))
    password.send_keys("")
    submit = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="submitButton"]'))
        )
    submit.click()
    time.sleep(1)

login()

WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "Programma's"))).click()

driver.get("https://portal.bingel.secure.malmberg.nl/leerkracht/pp4/35c96f86-c75a-40ff-a1b5-711486f2367b")



WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-product-group[2]/div/div[1]/div/ul/li/a'))).click()
driver.switch_to.window(driver.window_handles[1])
#klas aanklikken
WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "/html/body/p1-app/p1-groups/p1-card-container/p1-link-card/section/div"))).click()
#lesgeven
WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-menu/div[1]/a[3]'))).click()
#Naar blokken overzicht
WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-navbar/div[1]/div/a'))).click()
# kliken op blokken
aantal_blokken = len(driver.find_elements(By.XPATH, '//p1-card-container/p1-card')) + 1
for num in range(1,aantal_blokken):
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, f'//p1-card-container/p1-card[{num}]'))).click()
    time.sleep(1)
    # week 1 aanklikken.
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//p1-sidebar/div[2]/p1-progress-list-item[1]/div/a'))).click()
    #blokinfo
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-tabs/a[2]'))).click()
    naam_blok = driver.find_element(By.XPATH, '//p1-navbar/div[2]/div/h2').text
    #handleiding
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-document/div/ul[2]/li[1]/p/span/a/span'))).click()
    #weer een nieuw venster
    driver.switch_to.window(driver.window_handles[2])
    time.sleep(1)
    aantal_paginas = (int(driver.find_element(By.XPATH, '//*[@id="progress_indicator"]/span/span[3]').text))-1
    plaatjes = []
    for page in range(aantal_paginas):
        try:
            plaatjes.append(driver.find_element(By.XPATH, '//*[@id="print"]/img').get_attribute("src"))
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="next_slide"]'))).click()
            time.sleep(1)
        except:
            print("failed")

    plaatjes_new = [sub.replace('at800', 'at1600') for sub in plaatjes]

    save_path = Path.cwd() / f"{naam_blok}_plaatjes"
    save_path.mkdir(exist_ok=True)

    for num, url_plaatje in enumerate(plaatjes_new):
        response = requests.get(url_plaatje)
        if response.status_code == 200:
            time.sleep(0.2)
            with open(f"{save_path/naam_blok}_page_{num}.jpg", 'wb') as f:
                f.write(response.content)


    pictures = [str(p) for p in Path.cwd().glob(f"{naam_blok}_plaatjes/{naam_blok}*.jpg")]
    with open(f"{naam_blok}.pdf","wb") as f:
        f.write(img2pdf.convert(pictures))

    driver.close()
    driver.switch_to.window(driver.window_handles[1])
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//p1-navbar/div[1]/div/a'))).click()