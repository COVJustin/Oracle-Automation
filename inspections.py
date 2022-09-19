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
    central_user = "usr"
    central_pass = "pass"
    
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

    driver.switch_to.frame("FRMPERMIT")

    # Click edit
    edit = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnEdit']")
    edit.click()

    time.sleep(5)

    # Permit Info
    status = "ISSUED"
    desc = "Unit # 155 Unit was damaged by fire BP-2022-0788"
    applyDate = "5/13/22"
    expDate = "7/19/23"
    issueDate = "7/19/22"

    # Change Status
    firstLetter = status[0]
    driver.find_element(By.XPATH, "//input[@id = 'ctl09_C_ctl00_ddStatus_Input']").send_keys(firstLetter)
    
    # Change Dates 
    applyDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calAppliedDate$dateInput']")
    applyDateField.send_keys(Keys.CONTROL + "a")
    applyDateField.send_keys(Keys.DELETE)
    applyDateField.send_keys(applyDate)

    expDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calOtherDate1$dateInput']")
    expDateField.send_keys(Keys.CONTROL + "a")
    expDateField.send_keys(Keys.DELETE)
    expDateField.send_keys(expDate)

    issDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calIssuedDate$dateInput']")
    issDateField.send_keys(Keys.CONTROL + "a")
    issDateField.send_keys(Keys.DELETE)
    issDateField.send_keys(issueDate)
    
    # Change Description
    descField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$txtDescription']")
    descField.send_keys(Keys.CONTROL + "a")
    descField.send_keys(Keys.DELETE)
    descField.send_keys(desc)

    save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
    save.click()

    print('program finished')

central_login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', driver_setup(), 'BP22-00690')
