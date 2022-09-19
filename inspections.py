from gettext import find
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import csv
from threading import Thread
import pyautogui as pg

# Setups Selenium WebDriver
def driver_setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True) 
    driver = webdriver.Chrome(options = options)
    return driver

# function to log into Central Square andsearch permits
def central_login(url, driver, permit):

    print("logging in to Central Square....")
    driver.get(url)
    driver.maximize_window()
    central_user = #User name
    central_pass = #Password
    
    login = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtUID"]'))
            )
    
    password = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtPWD"]'))
            )

    button = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="btnSignIn"]'))
            )
    login.send_keys(central_user)
    password.send_keys(central_pass)
    button.click()

    central_search = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtSearch"]'))
            ) 
    central_search.send_keys(permit)
    central_search.send_keys(Keys.ENTER)

    time.sleep(8)

    print("successfully logged in")

    
    # pyautoGUI to access inspections tab
    print(pg.moveTo(330, 1032))
    print(pg.click())

    time.sleep(10)

    
    value = driver.find_element(By.XPATH, '//*[@id="ctl08_ddInspector_Arrow"]')
    value.click()
   

    print(value)
   



    print('program finished')

    

central_login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', driver_setup(), 'BP-2021-1431')
