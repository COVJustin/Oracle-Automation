from gettext import find
from selenium import webdriver
import chromedriver_binary
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

def permexist(driver, permit, permitFileLocation, permtype, permsubtype):
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
        try:
            permitframe = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "rwGlobalSearch"))
                        )
            driver.switch_to.frame(permitframe)
            driver.find_element(By.XPATH, "//a[contains(text(),'" + permit + "')]").click()
            driver.switch_to.parent_frame()
        except NoSuchElementException:
            driver.switch_to.parent_frame()
            with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'r') as zin:
                with zin.open(permit + " Information.csv") as infofile:
                    inforeader = pd.read_csv(infofile)
                    infoData = pd.DataFrame(inforeader)
                parcel = str(infoData.at[0, 'Parcel ID']).replace("-", "")
                parceladdr = str(infoData.at[0, 'Parcel Address'])
                cdesc =infoData.at[0, 'Central Square Description'] 
                parcel = parcel.zfill(10)
            noparcel = False
            central_search.send_keys(Keys.CONTROL + "a")
            central_search.send_keys(Keys.DELETE)
            if parcel != "0000000nan":
                central_search.send_keys(parcel)
            else:
                central_search.send_keys("0055160120")
                noparcel = True
            central_search.send_keys(Keys.ENTER)
            parcelframe = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "rwGlobalSearch"))
                        )
            time.sleep(7.5)
            searchcheck2 = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='RadWindowWrapper_rwGlobalSearch']"))
                )
            if searchcheck2.is_displayed():
                driver.switch_to.frame(parcelframe)
                if noparcel:
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_cboGroup_Input']"))
                        ).click()
                    time.sleep(1)
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'Land Management')]"))
                        ).click()
                else:
                    potparcels = driver.find_elements(By.XPATH, "//a[contains(text(),'" + parcel + "')]")
                    parcelfound = False
                    for potential in potparcels:
                        if parcelfound == False:
                            potentialparent = potential.find_element(By.XPATH, "../..")
                            try:
                                potentialparent.find_element(By.XPATH, ".//td[contains(text(),\"" + parceladdr + "\")]")
                                potential.click()
                                parcelfound = True
                            except NoSuchElementException:
                                ""
                    if parcelfound == False:
                        WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'" + parcel + "')]"))
                            ).click()
                driver.switch_to.parent_frame()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'FRMLAND'))
                    )
            driver.switch_to.frame("FRMLAND")
            time.sleep(3)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='ctl16_C_ctl00_radActionsMenu']/ul/li/a/img"))
                    ).click()
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Add Record')]"))
                    ).click()
            driver.switch_to.parent_frame()
            recordframe = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
            driver.switch_to.frame(recordframe)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboRecType_Input']"))
                    ).click()
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'Permit linked to this record')]"))
                    ).click()
            time.sleep(2)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboType_Input']"))
                    ).click()
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + permtype + "')]"))
                    ).click()
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, "//input[@id='ctl08_cboSubType_Input']").click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + permsubtype + "')]"))
                        ).click()
                time.sleep(2)
            except NoSuchElementException:
                ""
            recorddesc = WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_txtDesc']"))
                    )
            recorddesc.send_keys(cdesc)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_ImageButton1']"))
                    ).click()
            driver.switch_to.parent_frame()
            infloadcheck(driver)
            time.sleep(5)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                    )
            if noparcel:
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='ctl09_C_ctl00_radGeoActionsMenu']/ul/li/a/img"))
                    ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='ctl09_C_ctl00_radGeoActionsMenu']/ul/li/div/ul/li[4]/a/span"))
                    ).click()
                driver.switch_to.parent_frame()
                time.sleep(2)
                breakframe = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "rw"))
                        )
                driver.switch_to.frame(breakframe)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                        ).click()
                driver.switch_to.parent_frame()
                infloadcheck(driver)
            feerows = driver.find_elements(By.XPATH, "//table[@id='ctl12_C_ctl00_rGridFees_ctl00']/tbody/tr")
            feecount = 0
            if len(feerows) > 1:
                feecount = int(len(feerows) / 2)
            driver.switch_to.parent_frame()
            for i in range(feecount):
                time.sleep(1)
                infloadcheck(driver)
                feerow = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='ctl12_C_ctl00_rGridFees_ctl00_ctl04_radParentActionsMenu']/ul/li/a/img"))
                            )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'})", feerow)
                feerow.click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Delete Item')]"))
                            ).click()
                driver.switch_to.parent_frame()
                voidframe = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "rw"))
                            )
                driver.switch_to.frame(voidframe)
                WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                            ).click()
                driver.switch_to.parent_frame()
            infloadcheck(driver)
            inspcount = driver.find_elements(By.CLASS_NAME, "Inspections-ListItem")
            for i in range(len(inspcount)):
                insprow = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='ctl14_C_ctl00_rlvInspections_ctrl0_radInspectionsMenu']/ul/li/a/img"))
                            )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'})", insprow)
                insprow.click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Void Inspection')]"))
                            ).click()
                driver.switch_to.parent_frame()
                voidframe = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "rw"))
                            )
                driver.switch_to.frame(voidframe)
                WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                            ).click()
                driver.switch_to.parent_frame()
                infloadcheck(driver)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='ctl14_C_ctl00_rlvInspections_ctrl0_radInspectionsMenu']/ul/li/a/img"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Delete Inspection')]"))
                        ).click()
                driver.switch_to.parent_frame()
                voidframe = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "rw"))
                            )
                driver.switch_to.frame(voidframe)
                WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                            ).click()
                driver.switch_to.parent_frame()
                infloadcheck(driver)
            reviewcount = driver.find_elements(By.CLASS_NAME, "Reviews-ListItem")
            for i in range(len(reviewcount)):
                revrow = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='ctl15_C_ctl00_rlvReviews_ctrl0_radReviewsMenu']/ul/li/a/img"))
                            )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'})", revrow)
                revrow.click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Void Review')]"))
                            ).click()
                driver.switch_to.parent_frame()
                voidframe = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "rw"))
                            )
                driver.switch_to.frame(voidframe)
                WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                            ).click()
                driver.switch_to.parent_frame()
                infloadcheck(driver)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='ctl15_C_ctl00_rlvReviews_ctrl0_radReviewsMenu']/ul/li/a/img"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Delete Review')]"))
                        ).click()
                driver.switch_to.parent_frame()
                voidframe = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "rw"))
                            )
                driver.switch_to.frame(voidframe)
                WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                            ).click()
                driver.switch_to.parent_frame()
                infloadcheck(driver)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    try:
        WebDriverWait(driver, '5').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
    except TimeoutException:
        ""
            
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
def inputPR(driver, permit, permitFileLocation):
    z = zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip")
    if (permit + " Reviews.csv") in z.namelist():
        with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'r') as zin:
            prdata = io.StringIO(zin.read(permit + " Reviews.csv").decode('utf-8'))
            reader2 = csv.reader(prdata)
            reviewData = list(reader2)
        reviewData.pop(0)
        premadereviewcount = driver.find_elements(By.CLASS_NAME, "Reviews-ListItem")
        pmarray = []
        for i in range(len(premadereviewcount)):
            pmrevtype = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl15_C_ctl00_rlvReviews_ctrl" + str(i) + "_lblReviewType']/span"))
                        ).text
            pmcyclenum = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl15_C_ctl00_rlvReviews_ctrl" + str(i) + "_lblReviewGroup']/span[2]"))
                        ).text
            pmrev = pmrevtype[:18] + pmcyclenum[0]
            pmarray.append(pmrev)
        editcounter = 0
        for i in range(0, len(reviewData)):
            if (reviewData[i][2][:18] + reviewData[i][0]) not in pmarray:
                try:
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                            ).click()
                except ElementClickInterceptedException:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(2)
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                            ).click()
                driver.switch_to.parent_frame()
                innerframe = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(innerframe)
                if str(reviewData[i][2]) != "VALLEJO POLICE":
                    cycleexpand = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div/ul/li[" + str(eval('3 + ' + str(reviewData[i][0]))) + "]/div/span[2]/../.."))
                            )
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//div/ul/li[" + str(eval('3 + ' + str(reviewData[i][0]))) + "]/div/span[2]"))
                            ).click()
                    time.sleep(1)
                    WebDriverWait(cycleexpand, '45').until(
                            EC.element_to_be_clickable((By.XPATH, ".//span[text()='" + str(reviewData[i][2]) + "']"))
                            ).click()
                else:
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@id='ctl08_treeReviews']/ul/li/div/span[2]"))
                            ).click()
                    time.sleep(1)
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'VALLEJO POLICE')]"))
                            ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_ddContactName_Input']"))
                        ).click()
                try:
                    time.sleep(2.5)
                    driver.find_element(By.XPATH, "//li[contains(.,'" + reviewData[i][3].upper() + "')]").click()
                except NoSuchElementException:
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//a[@id='ctl08_ddContactName_Arrow']"))
                        ).click()
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_ddStatus_Input']"))
                        ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + reviewData[i][5] + "')]"))
                        ).click()
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calSentDate_dateInput']"))
                        )
                sentDateField = driver.find_element(By.XPATH, "//input[@id='ctl08_calSentDate_dateInput']")
                sentDateField.send_keys(Keys.CONTROL + "a")
                sentDateField.send_keys(Keys.DELETE)
                sentDateField.send_keys(reviewData[i][1])
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calDueDate_dateInput']"))
                        )
                dueDateField = driver.find_element(By.XPATH, "//input[@id='ctl08_calDueDate_dateInput']")
                dueDateField.send_keys(Keys.CONTROL + "a")
                dueDateField.send_keys(Keys.DELETE)
                dueDateField.send_keys(reviewData[i][4])
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_txtRemarks']"))
                        )
                remarks = driver.find_element(By.XPATH, "//input[@id='ctl08_txtRemarks']")
                remarks.send_keys("transferred from oracle (program)")
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[@id='ctl08_txtNote']"))
                        )
                note = driver.find_element(By.XPATH, "//textarea[@id='ctl08_txtNote']")
                note.send_keys(reviewData[i][7])
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                        ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)"))
                        ).click()
                infloadcheck(driver)
                try:
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl15_C_ctl00_rlvReviews_ctrl" + str(len(premadereviewcount) + editcounter) + "_btnEdit']"))
                        ).click()
                except ElementClickInterceptedException:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(2)
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl15_C_ctl00_rlvReviews_ctrl" + str(len(premadereviewcount) + editcounter) + "_btnEdit']"))
                        ).click()
                editcounter += 1
                driver.switch_to.parent_frame()
                innerframe2 = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(innerframe2)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calReceivedDate_dateInput']"))
                        )
                recDate = driver.find_element(By.XPATH, "//input[@id='ctl08_calReceivedDate_dateInput']")
                recDate.send_keys(Keys.CONTROL + "a")
                recDate.send_keys(Keys.DELETE)
                recDate.send_keys(reviewData[i][6])
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                        ).click()
                time.sleep(5)
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                        )
                driver.switch_to.frame("FRMPERMIT")

def inputDesc(driver, permit, permitFileLocation, permtype, permsubtype):
    with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'r') as zin:
            with zin.open(permit + " Information.csv") as infofile:
                inforeader = pd.read_csv(infofile)
                infoData = pd.DataFrame(inforeader)
            status = infoData.at[0, 'Status']
            desc = infoData.at[0, 'Central Square Description']
            bigdesc = infoData.at[0, 'Oracle Description']
            applyDate = infoData.at[0, 'Applied']
            expDate = infoData.at[0, 'Expired']
            issueDate = infoData.at[0, 'Issued']
            contname = infoData.at[0, 'Primary Contact']
            appname = infoData.at[0, 'Applicant']
            contnum = infoData.at[0, 'Primary Contact Phone']
            contemail = infoData.at[0, 'Primary Contact Email']
            if not permit.startswith("PW"):
                valuation = infoData.at[0, 'Valuation']
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)
    subtypeexist = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblPermitSubTypeNoEdit']"))
            ).text
    if subtypeexist == " " and permsubtype != "" and permtype != "":
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='ctl09_C_ctl00_radActionsMenu']/ul/li/a/img"))
                ).click()
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Edit Type/Subtype')]"))
                ).click()
        driver.switch_to.parent_frame()
        typeinner = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, 'rw'))
                )
        driver.switch_to.frame(typeinner)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboType_Input']"))
                ).click()
        time.sleep(2)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ permtype +"')]"))
                ).click()
        time.sleep(1)
        if permsubtype != "":
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboSubType_Input']"))
                    ).click()
            time.sleep(2)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ permsubtype +"')]"))
                    ).click()
            time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnPreSave']"))
                ).click()
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
        driver.switch_to.frame("FRMPERMIT")
    driver.switch_to.parent_frame()
    infloadcheck(driver)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()

    # Change Status
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
            ).click()
    time.sleep(1)
    try:
        WebDriverWait(driver, '5').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                ).click()
    except TimeoutException:
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl09_C_ctl00_btnRevert']"))
                ).click()
        time.sleep(3)
        driver.switch_to.parent_frame()
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
            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            )
        WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()
        WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
            ).click()
        time.sleep(1)
        WebDriverWait(driver, '5').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                ).click()
    # Change Dates 
    applyDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calAppliedDate$dateInput']")
    applyDateField.send_keys(Keys.CONTROL + "a")
    applyDateField.send_keys(Keys.DELETE)
    applyDateField.send_keys(applyDate)

    expDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calExpiredDate$dateInput']")
    expDateField.send_keys(Keys.CONTROL + "a")
    expDateField.send_keys(Keys.DELETE)
    expDateField.send_keys(expDate)

    if not permit.startswith("PW"):
        issDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calIssuedDate$dateInput']")
        issDateField.send_keys(Keys.CONTROL + "a")
        issDateField.send_keys(Keys.DELETE)
        issDateField.send_keys(issueDate)

    deleteApp = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calApprovedDate_dateInput']")
    deleteApp.send_keys(Keys.CONTROL + "a")
    deleteApp.send_keys(Keys.DELETE)

    deletePC = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calOtherDate1_dateInput']")
    deletePC.send_keys(Keys.CONTROL + "a")
    deletePC.send_keys(Keys.DELETE)
    
    # Change Description
    descField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$txtDescription']")
    descField.send_keys(Keys.CONTROL + "a")
    descField.send_keys(Keys.DELETE)
    descField.send_keys(desc)

    save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
    save.click()

    time.sleep(5)
    driver.switch_to.parent_frame()
    try:
        driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)").click()
    except NoSuchElementException:
        print("Valid date")
    try:
        time.sleep(5)
        innerframe3 = driver.find_element(By.NAME, 'rwEvents')
        driver.switch_to.frame(innerframe3)
        driver.find_element(By.XPATH, "//input[@id='btnNo0']").click()
        WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='btnClose']"))
            ).click()
        driver.switch_to.parent_frame()
    except NoSuchElementException:
        print("Valid expiration")
    WebDriverWait(driver, '45').until(
        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
        )
    driver.switch_to.frame("FRMPERMIT")
    time.sleep(5)
    WebDriverWait(driver, '45').until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
            )
    curstatus = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblStatus']"))
            ).text
    if curstatus != status:
        WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()
        # Change Status
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                ).click()
        time.sleep(1)
        WebDriverWait(driver, '5').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                ).click() 
        save2 = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']") 
        save2.click()
        time.sleep(5)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnAddNotes']"))
            ).click()
    driver.switch_to.parent_frame()
    noteinner = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.NAME, 'rw'))
            )
    driver.switch_to.frame(noteinner)
    notecount = len(driver.find_elements(By.XPATH, "//input[@title='Delete Note']"))
    descexist = False
    if notecount != 0:
        notecount = notecount / 2
        for notenumber in range(int(notecount)):
            notecontent = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='ctl08_rlvNotes_ctrl" + str(notenumber) + "_txtNoteEdit']"))
            ).text
            if notecontent == bigdesc:
                descexist = True
    if descexist == False:
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//textarea[@id='ctl08_txtNoteSave']"))
                ).send_keys(bigdesc)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnSave']"))
            ).click()
    driver.switch_to.parent_frame()
    infloadcheck(driver)
    time.sleep(3)
    WebDriverWait(driver, '45').until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
            )
    applicantexist = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblApplicantNameNoEdit']"))
            ).text
    if applicantexist == " ":
        try:
            applicantrow = WebDriverWait(driver, '10').until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(.,'APPLICANT')]/../../../../../../.."))
                )
            applicantedit = WebDriverWait(applicantrow, '45').until(
                EC.presence_of_all_elements_located((By.XPATH, "./child::td"))
                )
            WebDriverWait(applicantedit[2], '45').until(
                EC.presence_of_element_located((By.XPATH, ".//input"))
                ).click()
            driver.switch_to.parent_frame()
            applicantinner = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
            driver.switch_to.frame(applicantinner)
        except TimeoutException:
            WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl10_C_ctl00_btnAddContact']"))
                ).click()
            time.sleep(2)
            driver.switch_to.parent_frame()
            applicantinner = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
            driver.switch_to.frame(applicantinner)
            WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_ddContactType_Input']"))
                ).click()
            time.sleep(2)
            WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'APPLICANT')]"))
                ).click()
            time.sleep(1)
        nameentry = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_txtName']"))
                )
        nameentry.send_keys(Keys.CONTROL + "a")
        nameentry.send_keys(Keys.DELETE)
        nameentry.send_keys(appname)
        time.sleep(3)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'Create new')]"))
                ).click()
        time.sleep(2)
        if contname == appname:
            """
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_txtPhone']"))
                    ).click()
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_txtPhone']"))
                    ).send_keys(int(str(contnum).replace("+1", "").replace("(", "").replace(")", "").replace("-", "").replace(" ", "")))
            """
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_txtEmail']"))
                    ).send_keys(contemail)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnSave']"))
                ).click()
        time.sleep(2)
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
        driver.switch_to.frame("FRMPERMIT")
    time.sleep(2)
    
    # Change Valuation
    if not permit.startswith("PW"):
        try:
            driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnEditAllValuationsBottom']")
        except NoSuchElementException:
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$btnAddValuation']"))
                    ).click()
            driver.switch_to.parent_frame()
            innerframe4 = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
            driver.switch_to.frame(innerframe4)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                    )
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                    )
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//strong[contains(.,'JOB VALUATION = $1.00/EA')]"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                    ).click()
            driver.switch_to.parent_frame()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
            driver.switch_to.frame("FRMPERMIT")
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$rGridValuations$ctl00$ctl04$txtParentQty']"))
                    )
            time.sleep(4)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$rGridValuations$ctl00$ctl04$txtParentQty']"))
                    ).send_keys(valuation)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnSaveAllValuationsTop']"))
                    ).click()
            time.sleep(7.5)

def inputFees(driver, permit, permitFileLocation, permtype, permsubtype):
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//a[@id='ctl12_C_ctl00_lnkFeesPaid']"))
            )
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//a[@id='ctl12_C_ctl00_lnkBtnFeesDue']"))
            )
    try:
        driver.find_element(By.XPATH, "//input[@id = 'ctl12_C_ctl00_imgBtnEditAllFeesBottom']")
    except NoSuchElementException:
        z = zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip")
        if (permit + " Fees.csv") in z.namelist():
            with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'r') as zin:
                f = io.StringIO(zin.read(permit + " Fees.csv").decode('utf-8'))
                reader = csv.reader(f)
                data = list(reader)
            data.pop(0)
            totalrefund = 0.0
            refundnote = ""
            paydate = ""
            dueFees = []
            for i in range(len(data)):
                if data[i][6] != "":
                    paydate = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', data[i][6])[0]
                if data[i][3] == "REFUND" or data[i][3] == "REFNDP":
                    data[i][1].strip(" ")
                    found = False
                    maxnum = 0.0
                    maxfeeindex = 0
                    for j in range(len(data)):
                        if (float(data[j][1]) == float(data[i][1])) and (data[j][0] == data[j][0]) and (found == False) and data[j][3] == "PAID":
                            found = True
                            data[j][1] = str(0.0)
                            totalrefund += float(data[i][1])
                            refundnote += data[i][0].partition(" = ")[0] + ": -" + data[i][1] + "\n"
                            data[i][0] = "DELETE"
                        if (data[j][0] == data[i][0]) and found == False and data[j][3] == "PAID":
                            if float(data[j][1]) > maxnum:
                                maxnum = float(data[i][1])
                                maxfeeindex = j
                    if found == False:
                        tempfee = float(data[maxfeeindex][1]) - float(data[i][1])
                        data[maxfeeindex][1] = str(tempfee)
                        totalrefund += float(data[i][1])
                        refundnote += data[i][0].partition(" = ")[0] + ": -" + data[i][1] + "\n"
                        data[i][0] = "DELETE"
                elif data[i][3] == "DUE":
                    dueFees.append(data[i][0] + "§" + data[i][1])
            data = [i for i in data if i[0] != "DELETE"]
            keywrds = [item[0] for item in data]
            dupes = {value : [y for y, v in enumerate(keywrds) if value == v] for value in set(keywrds)}
            streetclosuredupes = {}
            if "STREET CLOSURE PERMIT - NON RES = QTY*581" in dupes:
                streetclosuredupes["STREET CLOSURE PERMIT - NON RES = QTY*581"] = dupes["STREET CLOSURE PERMIT - NON RES = QTY*581"]
                dupes.pop("STREET CLOSURE PERMIT - NON RES = QTY*581")
            if "STREET CLOSURE PERMIT - NON RES TECHNOLOGY SURCHARGE = QTY*23" in dupes:
                streetclosuredupes["STREET CLOSURE PERMIT - NON RES TECHNOLOGY SURCHARGE = QTY*23"] = dupes["STREET CLOSURE PERMIT - NON RES TECHNOLOGY SURCHARGE = QTY*23"]
                dupes.pop("STREET CLOSURE PERMIT - NON RES TECHNOLOGY SURCHARGE = QTY*23")
            if "STREET CLOSURE PERMIT - NON RES  COORDINATION CHARGE = QTY*17" in dupes:
                streetclosuredupes["STREET CLOSURE PERMIT - NON RES  COORDINATION CHARGE = QTY*17"] = dupes["STREET CLOSURE PERMIT - NON RES  COORDINATION CHARGE = QTY*17"]
                dupes.pop("STREET CLOSURE PERMIT - NON RES  COORDINATION CHARGE = QTY*17")
            if len(dupes) > 0:
                loopcount = max(len(v) for k,v in dupes.items())
                for j in range(loopcount):
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                            )
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
                        )
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
                        ).click()
                    driver.switch_to.parent_frame()
                    innerframe5 = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                    driver.switch_to.frame(innerframe5)
                    time.sleep(3)
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                        )
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                        )
                    for fee in dupes:
                        if j < len(dupes[fee]):
                            WebDriverWait(driver, '45').until(
                                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'" + fee + "')]"))
                                        ).click()
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                            ).click()
                    driver.switch_to.parent_frame()
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@class='TelerikModalOverlay']"))
                            )
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                            )
                    driver.switch_to.frame("FRMPERMIT")
                    driver.switch_to.parent_frame()
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                            )
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                            )
                    driver.switch_to.frame("FRMPERMIT")
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnCancelEditAllFeesBottom']"))
                        ).click()
                time.sleep(2)
            if len(streetclosuredupes) > 0:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(5)
                streetloopcount = max(len(v) for k,v in streetclosuredupes.items())
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@id='ctl09_C_ctl00_radActionsMenu']/ul/li/a/img"))
                        ).click()
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Edit Type/Subtype')]"))
                        ).click()
                driver.switch_to.parent_frame()
                typeinner = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(typeinner)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboType_Input']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'STREET CLOSURE')]"))
                        ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboSubType_Input']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'COMMUNITY')]"))
                        ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnPreSave']"))
                        ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
                driver.switch_to.frame("FRMPERMIT")
                time.sleep(2)
                for j in range(streetloopcount):
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                            )
                    time.sleep(2)
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
                        )
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
                        ).click()
                    driver.switch_to.parent_frame()
                    innerframe5 = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                    driver.switch_to.frame(innerframe5)
                    time.sleep(3)
                    WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                        )
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
                        )
                    for fee in streetclosuredupes:
                        if j < len(streetclosuredupes[fee]):
                            WebDriverWait(driver, '45').until(
                                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'" + fee + "')]"))
                                        ).click()
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                            ).click()
                    driver.switch_to.parent_frame()
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@class='TelerikModalOverlay']"))
                            )
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                            )
                    driver.switch_to.frame("FRMPERMIT")
                    driver.switch_to.parent_frame()
                    WebDriverWait(driver, '45').until(
                            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                            )
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                            )
                    driver.switch_to.frame("FRMPERMIT")
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnCancelEditAllFeesBottom']"))
                        ).click()
                time.sleep(2)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@id='ctl09_C_ctl00_radActionsMenu']/ul/li/a/img"))
                        ).click()
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Edit Type/Subtype')]"))
                        ).click()
                driver.switch_to.parent_frame()
                typeinner = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(typeinner)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboType_Input']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + permtype + "')]"))
                        ).click()
                time.sleep(1)
                if permsubtype != "":
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboSubType_Input']"))
                            ).click()
                    time.sleep(2)
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + permsubtype + "')]"))
                            ).click()
                    time.sleep(1)
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnPreSave']"))
                        ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
                driver.switch_to.frame("FRMPERMIT")
                time.sleep(2)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnEditAllFeesBottom']"))
                    )
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            driver.find_element(By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnEditAllFeesBottom']").click()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
                    )
            for i in range(0, len(data)):
                keywrds = [item[0].partition(" = ")[0].replace(" (enter amount)", "") for item in data]
                dupes = {value.partition(" = ")[0].replace(" (enter amount)", "") : [j for j, v in enumerate(keywrds) if value == v] for value in set(keywrds)}
                listofSiblings = driver.find_elements(By.XPATH, "//a[text()='" + data[i][0].partition(" = ")[0].replace(" (enter amount)", "") +"']")
                tempDic = {}
                count = 0
                for h in listofSiblings:
                    if "ParentFeeDescription" in h.get_attribute('id') and data[i][0].partition(" = ")[0].replace(" (enter amount)", "") == "STATE-BUILDING STANDARDS FEE":
                        print("skipped")
                    else:
                        tempDic[dupes[data[i][0].partition(" = ")[0].replace(" (enter amount)", "")][count]] = h.get_attribute('id')
                        count += 1
                siblingType = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.ID, tempDic[i]))
                        )
                sibRow = siblingType.find_element(By.XPATH, "..")
                sibRow2 = sibRow.find_element(By.XPATH, "..")
                siblingFeeInput = WebDriverWait(sibRow2, '20').until(
                        EC.presence_of_element_located((By.XPATH, ".//input[contains(@id,'FeeAmount')]"))
                        )
                siblingFeeInput.send_keys(Keys.CONTROL + "a")
                siblingFeeInput.send_keys(Keys.DELETE)
                siblingFeeInput.send_keys(data[i][1])                    
            driver.switch_to.parent_frame()
            time.sleep(2)
            try:
                WebDriverWait(driver, '10').until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)"))
                        ).click()
            except TimeoutException:
                ""
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
            driver.switch_to.frame("FRMPERMIT")
            total = 0
            for i in range(0, len(data)):
                total += float(data[i][1])
            curSum = driver.find_element(By.XPATH, "//a[@id='ctl12_C_ctl00_lnkBtnFeesDue']").text
            while math.isclose(total, float(curSum.replace(",","").replace("$",""))) == False:
                time.sleep(5)
                curSum = driver.find_element(By.XPATH, "//a[@id='ctl12_C_ctl00_lnkBtnFeesDue']").text
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
                    ).click()
            time.sleep(2)
            WebDriverWait(driver, '45').until(
                    EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                    )
            if totalrefund > 0:
                time.sleep(2)
                refundnote = "TOTAL REFUND AMOUNT: " + str(totalrefund) + "\n\nREFUND BREAKDOWN:\n" + refundnote
                WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl16_C_ctl00_btnAddAction']"))
                    ).click()
                driver.switch_to.parent_frame()
                chronoframe = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
                driver.switch_to.frame(chronoframe)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(.,'REFUND REQUEST-PROCESSED')]"))
                    )
                WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'REFUND REQUEST-PROCESSED')]"))
                    ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@id='ctl08_txtActionNotes']"))
                    ).send_keys(refundnote)
                WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnSave']"))
                    ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
                driver.switch_to.frame("FRMPERMIT")
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                        )
            time.sleep(5)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='ctl12_C_ctl00_imgBtnPayFees']"))
                    ).click()
            driver.switch_to.parent_frame()
            payout = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, 'rw'))
                )
            driver.switch_to.frame(payout)
            time.sleep(2)
            if len(dueFees) > 0:
                for due in dueFees:
                    foundMatch = False
                    tempArr = due.split("§")
                    temparrfee = tempArr[0].partition(' = ')[0]
                    potDues = driver.find_elements(By.XPATH, "//span[contains(.,'" + temparrfee + "')]/../..")
                    for potential in potDues:
                        if foundMatch == False:
                            potentialamount = WebDriverWait(potential, '45').until(
                                EC.presence_of_element_located((By.XPATH, ".//span[contains(.,'$')]"))
                                ).text
                            if float(potentialamount[1:].replace(",","")) == float(tempArr[1]):
                                WebDriverWait(potential, '45').until(
                                    EC.presence_of_element_located((By.XPATH, ".//input[@type='image']"))
                                    ).click()
                                foundMatch = True
                                time.sleep(2)
            time.sleep(2)
            nextbtn = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_imgBtnNext']"))
                    )
            if nextbtn.get_attribute("disabled") == "true":
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_imgBtnCancel']"))
                    ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
                driver.switch_to.frame("FRMPERMIT")
            else:
                nextbtn.click()
                time.sleep(3)
                finalpayout = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, 'FRMPAY'))
                    )
                driver.switch_to.frame(finalpayout)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='rcmboPaidBy_Input']"))
                    ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='rcmboPaidBy_DropDown']/div/ul/li"))
                    ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='rcmboPayMethod_Input']"))
                    ).click()
                time.sleep(1)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//li[contains(.,'CREDIT CARD')]"))
                    ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='txtConfirmationNo']"))
                    ).send_keys("Paid in Oracle")
                paydateinput = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='calPaidDate_dateInput']"))
                    )
                paydateinput.send_keys(Keys.CONTROL + "a")
                paydateinput.send_keys(Keys.DELETE)
                paydateinput.send_keys(paydate)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='imgBtnPaySupport']"))
                    ).click()
                time.sleep(3)
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='btnClose']"))
                    ).click()
                driver.switch_to.parent_frame()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                    )
                driver.switch_to.frame("FRMPERMIT")
                time.sleep(5)
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            time.sleep(5)
    
def inputIns(driver, permit, permitFileLocation):
    z = zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip")
    if (permit + " Inspection.csv") in z.namelist():
        with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'r') as zin:
            f = io.StringIO(zin.read(permit + " Inspection.csv").decode('utf-8'))
            reader = csv.reader(f)
            insData = list(reader)
        insData.pop(0)
        premadeinspectioncount = driver.find_elements(By.CLASS_NAME, "Inspections-ListItem")
        pmarray = []
        for i in range(len(premadeinspectioncount)):
            pminstype = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl14_C_ctl00_rlvInspections_ctrl" + str(i) + "_lblInspectionType']"))
                        ).text
            pmres = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl14_C_ctl00_rlvInspections_ctrl" + str(i) + "_lblResult']/span[2]"))
                        ).text
            pmsch = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl14_C_ctl00_rlvInspections_ctrl" + str(i) + "_lblScheduledDate']/span[2]"))
                        ).text
            pm = pminstype[:17] + pmres + pmsch
            pmarray.append(pm)
        editcounter = 0
        status = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblStatus']"))
                ).text
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(2)
        WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                ).click()
        try:
            time.sleep(1)
            WebDriverWait(driver, '5').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'ISSUED')]"))
                ).click()
        except TimeoutException:
            WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl09_C_ctl00_btnRevert']"))
                ).click()
            time.sleep(3)
            driver.switch_to.parent_frame()
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
                EC.presence_of_element_located((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
                )
            WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
                ).click()
            WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                ).click()
            time.sleep(1)
            WebDriverWait(driver, '5').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'ISSUED')]"))
                    ).click()
            time.sleep(1)
        save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
        save.click()
        time.sleep(5)
        insResultDic = {"": "",
                        "APPROVED": "APPROVED",
                        "NOT APPROVED": "NOT APPROVED",
                        "CORRECTIONS": "CORRECTIONS",
                        "RECHEDULED": "CANCELED",
                        "RESCHEDULED": "CANCELED",
                        "FINAL": "FINAL",
                        "NOT READY": "NOT READY",
                        "PARTIAL-NOTES": "PARTIAL",
                        "FOLLOW UP": "FOLLOW-UP",
                        "NEED ACCESS": "CANT GAIN ACCESS",
                        "PRE-FINAL APPR": "FINAL",
                        "PARTIAL": "PARTIAL",
                        "STOP WORK": "STOP WORK",
                        "POSTED NOTICE": "POSTED TAG",
                        "CORRECTION": "CORRECTIONS",
                        "CONDITIONS": "CONDITIONS",
                        "NO ACCESS": "CANT GAIN ACCESS",
                        "COMPLIANT": "APPROVED",
                        "NOV": "VIOLATION",
                        "INCOMPLETE": "CORRECTIONS",
                        "NOT NOTIFIED": "NOT READY",
                        "DEFICIENT": "CORRECTIONS",
                        "NON-STANDARD": "FAILED",
                        "WARNING/ NOTICE": "POSTED TAG",
                        "POSTPONED": "CANCELLED"
        }             
        for row in range(len(insData)):
            tempstatus = insData[row][2].upper()
            if tempstatus != "CANCELED" and tempstatus != "PENDING":
                tempstatus = insResultDic[insData[row][17].upper()]
            sch = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', insData[row][15])
            if len(sch) > 0:
                tempsch = sch[0][:-2] + "20" + sch[0][-2:]
            else:
                tempsch = "(mm/dd/yy)"
            if (insData[row][1][:17] + tempstatus + tempsch) not in pmarray:
                try:
                    WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl14_C_ctl00_btnAddInspection"]'))
                        ).click()
                except ElementClickInterceptedException:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(2)
                    WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl14_C_ctl00_btnAddInspection"]'))
                        ).click()
                time.sleep(3)
                driver.switch_to.parent_frame()
                innerframe = driver.find_element(By.NAME,'rw')
                driver.switch_to.frame(innerframe)

                inspect = insData[row][14].upper()
                sd = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', insData[row][15])
                scheduleDate = ""
                if len(sd) > 0:
                    scheduleDate = sd[0]
                st = re.findall('\d{1,2}[:]\d{2}', insData[row][15])
                scheduleTime = ""
                if len(st) > 0:
                    scheduleTime = st[0]
                    scheduleTime = dt.strptime(scheduleTime, "%H:%M")
                    scheduleTime = scheduleTime + (dt.min - scheduleTime) % timedelta(minutes=30)
                    if scheduleTime > dt.strptime("17:00", "%H:%M"):
                        scheduleTime = dt.strptime("17:00", "%H:%M")
                    elif scheduleTime < dt.strptime("7:00", "%H:%M"):
                        scheduleTime = dt.strptime("7:00", "%H:%M")
                    scheduleTime = scheduleTime.strftime("%I:%M %p")
                    if scheduleTime[0] == "0":
                        scheduleTime = scheduleTime[1:]
                cd = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', insData[row][16])
                completeDate = ""
                if len(cd) > 0:
                    completeDate = cd[0]
                ct = re.findall('\d{1,2}[:]\d{2}', insData[row][16])
                completeTime = ""
                if len(ct) > 0:
                    completeTime = ct[0]
                    completeTime = dt.strptime(completeTime, "%H:%M")
                    completeTime = completeTime + (dt.min - completeTime) % timedelta(minutes=30)
                    if completeTime > dt.strptime("17:00", "%H:%M"):
                        completeTime = dt.strptime("17:00", "%H:%M")
                    elif completeTime < dt.strptime("7:00", "%H:%M"):
                        completeTime = dt.strptime("7:00", "%H:%M")
                    completeTime = completeTime.strftime("%I:%M %p")
                    if completeTime[0] == "0":
                        completeTime = completeTime[1:]
                result = insData[row][17].upper()
                comments = insData[row][20]
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddInspector_Input"]'))
                        ).click()
                bppwdef = False
                try:
                    time.sleep(2.5)
                    driver.find_element(By.XPATH, "//li[contains(.,'"+ inspect +"')]").click()
                except NoSuchElementException:
                    if (permit.startswith("PW")):
                        WebDriverWait(driver, '20').until(
                            EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'PUBLIC WORKS INSPECTIONS BUCKET')]"))
                            ).click()
                    else:
                        WebDriverWait(driver, '20').until(
                            EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'BUILDING INSPECTIONS BUCKET')]"))
                            ).click()
                    bppwdef = True
                time.sleep(2)
                scheduled = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calScheduledDate$dateInput']"))
                        )
                scheduled.send_keys(Keys.CONTROL + "a")
                scheduled.send_keys(Keys.DELETE)
                scheduled.send_keys(scheduleDate)

                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$ddScheduleTime']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + scheduleTime + "')]"))
                        ).click()
                time.sleep(2)
                completed = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calCompletedDate$dateInput']"))
                        )
                completed.send_keys(completeDate)
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$ddCompletedTime']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + completeTime + "')]"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddResult_Input"]'))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl08_ddResult_Input"]'))
                        ).click()
                canceled = insData[row][2].upper()
                if canceled == "CANCELED" or canceled == "PENDING":
                    WebDriverWait(driver, '20').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ canceled +"')]"))
                    ).click()
                    time.sleep(2)
                else:
                    WebDriverWait(driver, '20').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ insResultDic[result] +"')]"))
                    ).click()
                    time.sleep(2)
                driver.find_element(By. XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/div/span[2]').click()
                time.sleep(1)
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='" + insData[row][1] + "']"))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_btnSave"]'))
                        ).click()
                time.sleep(1)
                driver.switch_to.parent_frame()
                try:
                    WebDriverWait(driver, '5').until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="modalPage"]/div[2]/div/div/table/tbody/tr/td/img[1]'))
                            ).click()
                    time.sleep(3)
                except TimeoutException:
                    ""
                if bppwdef == True:
                    WebDriverWait(driver, '45').until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                        )
                    try:
                        inspectioncap = driver.find_element(By.NAME, 'rwEvents')
                        driver.switch_to.frame(inspectioncap)
                        time.sleep(2)
                        try:
                            WebDriverWait(driver, '5').until(
                                EC.presence_of_element_located((By.XPATH, "//input[@id='btnYes0']"))
                                ).click()
                            time.sleep(2)
                            WebDriverWait(driver, '5').until(
                                EC.presence_of_element_located((By.XPATH, "//input[@id='btnClose']"))
                                ).click()
                            time.sleep(3)
                        except TimeoutException:
                            ""
                        driver.switch_to.parent_frame()
                    except NoSuchElementException:
                        ""
                WebDriverWait(driver, '45').until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                        )
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'FRMPERMIT'))
                        )
                driver.switch_to.frame("FRMPERMIT")
                time.sleep(1)
                if comments != "":
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl14_C_ctl00_rlvInspections_ctrl" + str(len(premadeinspectioncount) + editcounter) +"_btnEdit']"))
                            ).click()
                    driver.switch_to.parent_frame()
                    innerframe = driver.find_element(By.NAME,'rw')
                    driver.switch_to.frame(innerframe)
                    WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ctrlNotes_txtNoteSave"]'))
                        ).send_keys(comments)
                    time.sleep(1)
                    WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_btnSave"]'))
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
                editcounter += 1
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(2)
        WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                ).click()
        time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                ).click()
        save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
        save.click()
        time.sleep(5)

def inputAttach(driver, permit, permitFileLocation):
    z = zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip")
    attachcount = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='lblAttCount']/div/span"))
            ).text
    if (permit + " Attachments.zip") in z.namelist() and attachcount == str(0):
        with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", "r") as zfile:
            for name in zfile.namelist():
                if name == permit + " Attachments.zip":
                    zfiledata = io.BytesIO(zfile.read(name))
                    with zipfile.ZipFile(zfiledata) as zfile2:
                        filelist = zfile2.namelist()
                        zfile2.extractall(permitFileLocation)
                        for fileexists in filelist:
                            while os.path.exists(permitFileLocation + "/" + fileexists) == False:
                                time.sleep(2)
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
        filestring = ""
        cbcount = 0
        for filename in filelist:
            if not filename.endswith(".svg") and not filename.endswith(".HEIC") and not filename.endswith(".heic") and not filename.endswith(".DNG") and not filename.endswith(".geprint"):
                filestring += permitFileLocation + "/" + filename + " \n "
                cbcount += 1
        upload.send_keys(filestring.rstrip())
        checkboxes = WebDriverWait(driver, '45').until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']"))
                )
        while len(checkboxes) != cbcount:
            time.sleep(2)
            checkboxes = WebDriverWait(driver, '45').until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']"))
                )
        for cb in checkboxes:
            cb.click()
        time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='btnConfirm']"))
                ).click()
        for deletefile in filelist:
            os.remove(permitFileLocation + "/" + deletefile)
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

def transfer(url, driver, permit, permitFileLocation, central_user, central_pass, permtype, permsubtype, needDesc, needFees, needIns, needPR, needAttach):
    try:
        if os.path.exists(permit):
            with open(permit, "r") as permfile:
                permlines = permfile.readlines()
            permlines = (i.strip() for i in permlines)
            login(url, driver, central_user, central_pass)
            reset = 0
            for p in permlines:
                with open(permitFileLocation + "/00 Checked Permits.txt", "r") as checkfile:
                    checklines = checkfile.readlines()
                checklines = (i.strip() for i in checklines)
                if p not in checklines:
                    if reset == 15:
                        driver.close()
                        driver = driver_setup()
                        login(url, driver, central_user, central_pass)
                        reset = 0
                    with zipfile.ZipFile(permitFileLocation + "/" + p + ".zip", 'r') as zin:
                        with zin.open(p + " Information.csv") as infofile:
                            inforeader = pd.read_csv(infofile)
                            infoData = pd.DataFrame(inforeader)
                    if p.startswith("BP"):
                        rvc = infoData.at[0, "Residential/Commercial"]
                        if rvc == "RESIDENTIAL":
                            pt = "SINGLE FAMILY RESIDENTIAL"
                            pst = "ALTERATION/REMODEL"
                        else:
                            pt = "BUILDING COMMERCIAL"
                            pst = "ALTERATION/REMODEL"
                    elif p.startswith("EL"):
                        rvc = infoData.at[0, "Residential/Commercial"]
                        if rvc == "RESIDENTIAL":
                            pt = "ELECTRICAL RESIDENTIAL"
                            pst = "UP TO 324A"
                        else:
                            pt = "ELECTRICAL COMMERCIAL"
                            pst = "UP TO 324A"
                    elif p.startswith("ME"):
                        rvc = infoData.at[0, "Residential/Commercial"]
                        if rvc == "RESIDENTIAL":
                            pt = "MECHANICAL RESIDENTIAL"
                            pst = "FURNACE AND/OR AC ONLY"
                        else:
                            pt = "MECHANICAL COMMERCIAL"
                            pst = "EQUIPMENT"
                    elif p.startswith("PL"):
                        rvc = infoData.at[0, "Residential/Commercial"]
                        if rvc == "RESIDENTIAL":
                            pt = "PLUMBING RESIDENTIAL"
                            pst = "WATER HEATER"
                        else:
                            pt = "PLUMBING COMMERCIAL"
                            pst = "WATER HEATER REPLACEMENT"
                    elif p.startswith("PW"):
                        if infoData.at[0, 'Service Type'] == "ENCROACHMENT":
                            pt = "ENCROACHMENT"
                            pst = "Encroachment"
                        elif infoData.at[0, 'Service Type'] == "EXCAVATION":
                            pt ="EXCAVATION"
                            pst = "Utility Planned Proj"
                        elif infoData.at[0, 'Service Type'] == "ADDRESS CHANGE" or infoData.at[0, 'Service Type'] == "ADDRESS ASSIGNMENT":
                            pt = "OTHER SERVICES"
                            pst = "ADDRESS CHG/CRTN"
                        elif infoData.at[0, 'Service Type'] == "DREDGING" or infoData.at[0, 'Service Type'] == "GRADING":
                            pt = "GRADING"
                            pst = "Building Permit PW"
                        elif infoData.at[0, 'Service Type'] == "FULL ABANDONMENT" or infoData.at[0, 'Service Type'] == "PARTIAL ABANDONMENT":
                            pt = "ABANDONMENT OF RIGHT"
                            pst = ""
                        elif infoData.at[0, 'Service Type'] == "IMPROVEMENT":
                            pt = "IMPROVEMENT"
                            pst = "Building Permit PW"
                        elif infoData.at[0, 'Service Type'] == "SPECIAL EVENTS":
                            pt = "SPECIAL EVENTS"
                            pst = ""
                    permexist(driver, p, permitFileLocation, pt, pst)
                    status = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblStatus']"))
                        ).text
                    if needPR:
                        inputPR(driver, p, permitFileLocation)
                        if needDesc == False:
                            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                            time.sleep(2)
                            WebDriverWait(driver, '45').until(
                                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
                                ).click()
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                                    ).click()
                            time.sleep(1)
                            WebDriverWait(driver, '45').until(
                                    EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                                    ).click()
                            deleteApp = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calApprovedDate_dateInput']")
                            deleteApp.send_keys(Keys.CONTROL + "a")
                            deleteApp.send_keys(Keys.DELETE)
                            deletePC = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calOtherDate1_dateInput']")
                            deletePC.send_keys(Keys.CONTROL + "a")
                            deletePC.send_keys(Keys.DELETE)
                            save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
                            save.click()
                            time.sleep(5)
                    if needDesc:
                        inputDesc(driver, p, permitFileLocation, pt, pst)
                    if needIns:
                        inputIns(driver, p, permitFileLocation)
                    if needAttach:
                        inputAttach(driver, p, permitFileLocation)
                    if needFees:
                        inputFees(driver, p, permitFileLocation, pt, pst)
                    driver.switch_to.parent_frame()
                    with open(permitFileLocation + "/00 Checked Permits.txt", "a") as writecf:
                        writecf.write(p + "\n")
                    reset += 1
        else:
            login(url, driver, central_user, central_pass)
            permexist(driver, permit, permitFileLocation, permtype, permsubtype)
            status = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblStatus']"))
                    ).text
            if needPR:
                inputPR(driver, permit, permitFileLocation)
                if needDesc == False:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(2)
                    WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
                        ).click()
                    WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
                            ).click()
                    time.sleep(1)
                    WebDriverWait(driver, '45').until(
                            EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
                            ).click()
                    deleteApp = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calApprovedDate_dateInput']")
                    deleteApp.send_keys(Keys.CONTROL + "a")
                    deleteApp.send_keys(Keys.DELETE)
                    deletePC = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calOtherDate1_dateInput']")
                    deletePC.send_keys(Keys.CONTROL + "a")
                    deletePC.send_keys(Keys.DELETE)
                    save = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnSave']")
                    save.click()
                    time.sleep(5)
            if needDesc:
                inputDesc(driver, permit, permitFileLocation, permtype, permsubtype)
            if needIns:
                inputIns(driver, permit, permitFileLocation)
            if needAttach:
                inputAttach(driver, permit, permitFileLocation)
            if needFees:
                inputFees(driver, permit, permitFileLocation, permtype, permsubtype)
    except:
        driver.close()
        transfer(url, driver_setup(), permit, permitFileLocation, central_user, central_pass, permtype, permsubtype, needDesc, needFees, needIns, needPR, needAttach)
    print('program finished')
    return


