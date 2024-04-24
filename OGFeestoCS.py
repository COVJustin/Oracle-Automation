from gettext import find
from selenium import webdriver
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, TimeoutException
from datetime import datetime as dt
from datetime import timedelta
import re
import io
import zipfile
import math
import os
import time
import pandas as pd
import csv
from pyhtml2pdf import converter
from threading import Thread
import pyautogui as pg

# Setups Selenium WebDriver
def driver_setup():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True) 
    driver = webdriver.Chrome(options = options)
    return driver

# function to log into Central Square & Oracle and search permits
def login(url, driver, central_user, central_pass):
    print("logging in to Central Square....")
    driver.get(url)
    driver.maximize_window()
    
    login = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtUID"]'))
            )
    
    password = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtPWD"]'))
            )

    button = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="btnSignIn"]'))
            )
    login.send_keys(central_user)
    password.send_keys(central_pass)
    button.click()

    print("successfully logged in")

            
def infloadcheck(driver):
    try:
        time.sleep(2)
        WebDriverWait(driver, '10').until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                )
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
        time.sleep(2)
    except TimeoutException:
        driver.refresh()
        WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtSearch"]'))
            )
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='divIconWrapperPermit']"))
                ).click()
        time.sleep(2)
        WebDriverWait(driver, '45').until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                )
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, 'FRMPERMIT'))
                )
        driver.switch_to.frame("FRMPERMIT")
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                )
        time.sleep(2)

def inputAttach(driver, permit, permitFileLocation):
    z = zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip")
    if (permit + " Fees.csv") in z.namelist():
        central_search = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtSearch"]'))
            )
        central_search.send_keys(Keys.CONTROL + "a")
        central_search.send_keys(Keys.DELETE)
        central_search.send_keys(permit)
        central_search.send_keys(Keys.ENTER)
        searchcheck = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='RadWindowWrapper_rwGlobalSearch']"))
            )
        time.sleep(10)
        if searchcheck.is_displayed():
            permitframe = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "rwGlobalSearch"))
                        )
            driver.switch_to.frame(permitframe)
            driver.find_element(By.XPATH, "//a[contains(text(),'" + permit + "')]").click()
            driver.switch_to.parent_frame()
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
        with z as zfile:
            filelist = zfile.namelist()
            for fileexists in filelist:
                if fileexists.endswith("Fees.csv"):
                    zfile.extract(fileexists, permitFileLocation)
                    time.sleep(2)
                    pd.set_option('display.max_colwidth', None)
                    csvz = pd.read_csv(permitFileLocation + "/" + permit + " Fees.csv")
                    csvz.columns = pd.MultiIndex.from_product([[permit + " Fee Breakdown (Pulled from Oracle)"], csvz.columns])
                    csvz = csvz.style.set_properties(**{'font-size': '6pt'})
                    csvz.to_html(permitFileLocation + "/" + permit + " Fees.html")
                    converter.convert(permitFileLocation + "/" + permit + " Fees.html", permitFileLocation + "/" + permit + " Original Oracle Fees.pdf")
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".rainbowbutton:nth-child(2)"))
                ).click()
        time.sleep(2)
        driver.switch_to.parent_frame()
        attachframe = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "rw"))
                    )
        driver.switch_to.frame(attachframe)
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctrlWinAttachments1_btnUpload']"))
                ).click()
        time.sleep(3)
        upload = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='RadAsyncUpload1file0']"))
                )
        filestring = str(permitFileLocation + "/" + permit + " Original Oracle Fees.pdf")
        upload.send_keys(filestring.rstrip())
        checkboxes = WebDriverWait(driver, '45').until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']"))
                )
        for cb in checkboxes:
            cb.click()
        time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='btnConfirm']"))
                ).click()
        os.remove(permitFileLocation + "/" + permit + " Fees.csv")
        os.remove(permitFileLocation + "/" + permit + " Fees.html")
        os.remove(permitFileLocation + "/" + permit + " Original Oracle Fees.pdf")
        time.sleep(3)
        WebDriverWait(driver, '60').until(
                EC.presence_of_element_located((By.XPATH, "//img[@id='closeUpload']"))
                ).click()
        driver.switch_to.parent_frame()
        time.sleep(2)
        WebDriverWait(driver, '45').until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                )
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, 'FRMPERMIT'))
                )
        driver.switch_to.frame("FRMPERMIT")
        time.sleep(2)

def transfer(url, driver, permitList, permitFileLocation, central_user, central_pass):
    try:
        login(url, driver, central_user, central_pass)
        with open(permitList, "r", newline='', encoding='utf-8-sig') as csvf:
            csvreader = csv.reader(csvf)
            csvlist = list(csvreader)
        reset = 0
        for i in range(len(csvlist)):
            p = str(csvlist[i][0])
            with open(permitFileLocation + "/00 Checked Permits.txt", "r") as checkfile:
                checklines = checkfile.readlines()
            checklines = (i.strip() for i in checklines)
            if p not in checklines:
                if reset == 15:
                    driver.close()
                    driver = driver_setup()
                    login(url, driver, central_user, central_pass)
                    reset = 0
                inputAttach(driver, p, permitFileLocation)
                driver.switch_to.parent_frame()
                with open(permitFileLocation + "/00 Checked Permits.txt", "a") as writecf:
                    writecf.write(p + "\n")
                reset += 1

    except:
        driver.close()
        transfer(url, driver_setup(), permitList, permitFileLocation, central_user, central_pass)

listofallpermits = r"" #The location of the csv that has the list of every permit
permitfiledirectory = r"" #The folder directory location of all the permits
csuser = "" #Central Square username
cspass = "" #Central Square password

transfer(r"https://vall-trk.aspgov.com/CommunityDevelopment/TRAKiTMain.aspx?A=A&", driver_setup(), listofallpermits, permitfiledirectory, csuser, cspass)
print('program finished')



