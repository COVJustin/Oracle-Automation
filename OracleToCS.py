from gettext import find
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from datetime import datetime as dt
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
def login(url, driver, permit, central_user, central_pass):
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

    central_search = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="txtSearch"]'))
            ) 
    central_search.send_keys(permit)
    central_search.send_keys(Keys.ENTER)

    print("successfully logged in")

    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
    driver.switch_to.frame("FRMPERMIT")

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
                cycleexpand = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//div/ul/li[" + str(eval('3 + ' + str(reviewData[i][0]))) + "]/div/span[2]/../.."))
                        )
                WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//div/ul/li[" + str(eval('3 + ' + str(reviewData[i][0]))) + "]/div/span[2]"))
                        ).click()
                WebDriverWait(cycleexpand, '45').until(
                        EC.element_to_be_clickable((By.XPATH, ".//span[text()='" + str(reviewData[i][2]) + "']"))
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
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                        )
                driver.switch_to.frame("FRMPERMIT")
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
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()

    # Change Status
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
            ).click()
    time.sleep(1)
    WebDriverWait(driver, '45').until(
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

    issDateField = driver.find_element(By.XPATH, "//input[@name = 'ctl09$C$ctl00$calIssuedDate$dateInput']")
    issDateField.send_keys(Keys.CONTROL + "a")
    issDateField.send_keys(Keys.DELETE)
    issDateField.send_keys(issueDate)

    deleteApp = driver.find_element(By.XPATH, "//input[@id='ctl09_C_ctl00_calApprovedDate_dateInput']")
    deleteApp.send_keys(Keys.CONTROL + "a")
    deleteApp.send_keys(Keys.DELETE)
    
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
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnAddNotes']"))
            ).click()
    driver.switch_to.parent_frame()
    noteinner = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.NAME, 'rw'))
            )
    driver.switch_to.frame(noteinner)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//textarea[@id='ctl08_txtNoteSave']"))
            ).send_keys(bigdesc)
    WebDriverWait(driver, '45').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_btnSave']"))
            ).click()
    driver.switch_to.parent_frame()
    WebDriverWait(driver, '45').until(
        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
        )
    driver.switch_to.frame("FRMPERMIT")
    time.sleep(5)
    WebDriverWait(driver, '45').until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
            )
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
        time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ permtype +"')]"))
                ).click()
        time.sleep(1)
        WebDriverWait(driver, '45').until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl08_cboSubType_Input']"))
                ).click()
        time.sleep(1)
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
    applicantexist = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblApplicantNameNoEdit']"))
            ).text
    if applicantexist == " ":
        applicantrow = WebDriverWait(driver, '45').until(
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
    time.sleep(3)
    
    """
    # Change Valuation
    try:
        time.sleep(5)
        driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnEditAllValuationsBottom']").click()
    except NoSuchElementException:
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$btnAddValuation']"))
                ).click()
        driver.switch_to.parent_frame()
        innerframe4 = WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, 'rw'))
                )
        time.sleep(5)
        driver.switch_to.frame(innerframe4)
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//strong[contains(.,'JOB VALUATION = $1.00/EA')]"))
                ).click()
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                ).click()
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
    valField = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$rGridValuations$ctl00$ctl04$txtParentQty']"))
            )
    valField.send_keys(valuation)
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnSaveAllValuationsTop']"))
            ).click()
    """

def inputFees(driver, permit, permitFileLocation):
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
        for i in range(len(data)):
            if data[i][3] == "REFUND":
                data[i][1].strip(" ")
                found = False
                maxnum = 0.0
                maxfeeindex = 0
                paidlength = [x for x in data if x[3] == "PAID"]
                for j in range(len(paidlength)):
                    if (float(data[j][1]) == float(data[i][1])) and (data[j][0] == data[j][0]) and found == False:
                        found = True
                        data[j][1] = str(0.0)
                        totalrefund += float(data[i][1])
                        refundnote += data[i][0].partition(" = ")[0] + ": -" + data[i][1] + "\n"
                        data[i][0] = "DELETE"
                    if (data[j][0] == data[i][0]) and found == False:
                        if float(data[j][1]) > maxnum:
                            maxnum = float(data[i][1])
                            maxfeeindex = j
                if found == False:
                    tempfee = float(data[maxfeeindex][1]) - float(data[i][1])
                    data[maxfeeindex][1] = str(tempfee)
                    totalrefund += float(data[i][1])
                    refundnote += data[i][0].partition(" = ")[0] + ": -" + data[i][1] + "\n"
                    data[i][0] = "DELETE"
        data = [i for i in data if i[0] != "DELETE"]
        keywrds = [item[0] for item in data]
        dupes = {value : [y for y, v in enumerate(keywrds) if value == v] for value in set(keywrds)}
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
            time.sleep(5)
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
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnCancelEditAllFeesBottom']"))
                ).click()
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
            keywrds = [item[0].partition(" = ")[0] for item in data]
            dupes = {value.partition(" = ")[0] : [j for j, v in enumerate(keywrds) if value == v] for value in set(keywrds)}
            listofSiblings = driver.find_elements(By.XPATH, "//a[text()='" + data[i][0].partition(" = ")[0] +"']")
            tempDic = {}
            count = 0
            for h in listofSiblings:
                if "ParentFeeDescription" in h.get_attribute('id') and data[i][0].partition(" = ")[0] == "STATE-BUILDING STANDARDS FEE":
                    print("skipped")
                else:
                    tempDic[dupes[data[i][0].partition(" = ")[0]][count]] = h.get_attribute('id')
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
        WebDriverWait(driver, '45').until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)"))
                ).click()
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

    
def inputIns(driver, permit, permitFileLocation):               
    with open("Oracle-Automation/Permits/" + permit + " inspection.csv", "r", newline='') as csvfile:
        upperStream = (line.upper() for line in csvfile)
        inspections = csv.reader(upperStream)
        next(inspections)
        for row in inspections:
                driver.find_element(By.XPATH, "//input[@name = 'ctl14$C$ctl00$btnAddInspection']").click()
                time.sleep(3)
                driver.switch_to.parent_frame()
                innerframe = driver.find_element(By.NAME,'rw')
                driver.switch_to.frame(innerframe)

                inspect = row[14]
                scheduleDate = row[15]
                setDate = "Specified"
                scheduleTime = "8"
                completeDate = row[16]
                completeTime = "1"
                result = row[17]

                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddInspector_Input"]'))
                        ).click()
                time.sleep(1)
                try:
                        WebDriverWait(driver, '45').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ inspect +"')]"))
                        ).click()
                except:
                        WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddInspector_Input"]'))
                        ).click()
                time.sleep(2)

                defaultDate = setDate[0]
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddSetDefault_Input"]'))
                        ).send_keys(defaultDate)

                scheduled = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calScheduledDate$dateInput']"))
                        )
                scheduled.send_keys(Keys.CONTROL + "a")
                scheduled.send_keys(Keys.DELETE)
                scheduled.send_keys(scheduleDate)

                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$ddScheduleTime']"))
                        ).send_keys(scheduleTime)
                
                
                completed = WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calCompletedDate$dateInput']"))
                        )
                completed.send_keys(completeDate)

                secondTime = driver.find_element(By.XPATH, "//input[@name = 'ctl08$ddCompletedTime']")
                secondTime.send_keys(completeTime)

                res = result[0]
                finalResult= WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddResult_Input"]'))
                        )
                finalResult.send_keys(res)
        
                driver.find_element(By. XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/div/span[2]').click()
                if row[1] == '101 SURVEY/SET BACKS':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[66]/div/span[3]').click()
                elif row[1] == '102 UFER/GROUND ELECTRODE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[67]/div/span[3]').click()
                elif row[1] == '103 PIERS':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[68]/div/span[3]').click()
                elif row[1] == '104 FOOTINGS':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[69]/div/span[3]').click()
                elif row[1] == '105 SLAB FOUNDATIONS':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[70]/div/span[3]').click()
                elif row[1] == '106 SlAB GARAGE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[71]/div/span[3]').click()
                elif row[1] == '107 DRIVEWAY':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[72]/div/span[3]').click()
                elif row[1] == '108 DEMOLITION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[73]/div/span[3]').click()
                elif row[1] == '200 ROUGH GRADING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[75]/div/span[3]').click()
                elif row[1] == '201 FINISH GRADING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[76]/div/span[3]').click()
                elif row[1] == '202 GEN BLDG SITE/IN-PRO':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[77]/div/span[3]').click()
                elif row[1] == '300 MH SET-UP':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[78]/div/span[3]').click()
                elif row[1] == '301 MH ACCESSORY INSP':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[79]/div/span[3]').click()
                elif row[1] == '302 MH PERM FOUNDATION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[80]/div/span[3]').click()
                elif row[1] == '303 MH-FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[81]/div/span[3]').click()
                elif row[1] == '400 UNDERFLOOR FRAME':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[82]/div/span[3]').click()
                elif row[1] == '401 SHEAR NAIL-EXT':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[83]/div/span[3]').click()
                elif row[1] == '402 SHEAR NAIL-INT':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[84]/div/span[3]').click()
                elif row[1] == '403 ROOF DECK NAIL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[85]/div/span[3]').click()
                elif row[1] == '404 ROUGH FRAME':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[86]/div/span[3]').click()
                elif row[1] == '405 EXT. LATH/SLIDING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[87]/div/span[3]').click()
                elif row[1] == '406 DRYWALL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[88]/div/span[3]').click()
                elif row[1] == '407 FIREWALL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[89]/div/span[3]').click()
                elif row[1] == '408 GREEN/GRAY/PURPLE-BD':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[90]/div/span[3]').click()
                elif row[1] == '409 WET WALL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[91]/div/span[3]').click()
                elif row[1] == '410 STRUCTURAL MISC/T-BAR':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[92]/div/span[3]').click()
                elif row[1] == '411 ROOF/IN-PROGRESS':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[93]/div/span[3]').click()
                elif row[1] == '412 WINDOW REPLACEMENT':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[94]/div/span[3]').click()
                elif row[1] == '413 FIREWALL PENETRATION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[95]/div/span[3]').click()
                elif row[1] == '414 STRUCTURAL OTHER':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[96]/div/span[3]').click()
                elif row[1] == '501 CONDUIT/UNDERGROUND':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[98]/div/span[3]').click()
                elif row[1] == '502 SERVICE ENTRANCE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[99]/div/span[3]').click()
                elif row[1] == '503 ROUGH ELECTRICAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[100]/div/span[3]').click()
                elif row[1] == '504 BONDING/GROUNDING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[101]/div/span[3]').click()
                elif row[1] == '505 ELECTRIC RESTORE SERVICE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[102]/div/span[3]').click()
                elif row[1] == '507 ELECTRIC METER RELEASE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[103]/div/span[3]').click()
                elif row[1] == '600 UNDERFLOOR INSULATION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[105]/div/span[3]').click()
                elif row[1] == '601 FRAMING INSULATION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[106]/div/span[3]').click()
                elif row[1] == '602 CEILING INSULATION':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[107]/div/span[3]').click()
                elif row[1] == '700 GROUND PLUMBING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[108]/div/span[3]').click()
                elif row[1] == '701 UNDERFLOOR PLUMBING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[109]/div/span[3]').click()
                elif row[1] == '702 ROUGH PLUMBING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[110]/div/span[3]').click()
                elif row[1] == '703 SHOWER PAN TEST':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[111]/div/span[3]').click()
                elif row[1] == '704 WATER SERVICE/PIPING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[112]/div/span[3]').click()
                elif row[1] == '705 WATER HEATER':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[113]/div/span[3]').click()
                elif row[1] == '706 GAS PRESSURE TEST/PIPING':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[114]/div/span[3]').click()
                elif row[1] == '707 GAS METER RELEASE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[115]/div/span[3]').click()
                elif row[1] == '708 GAS RESTORE SERVICE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[116]/div/span[3]').click()
                elif row[1] == '801 CMU-LIFTS 1,2,3...':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[119]/div/span[3]').click()
                elif row[1] == '900 SITE CHECK/PRE-GUNITE':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[120]/div/span[3]').click()
                elif row[1] == '901 BOND CVTY/DECK':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[121]/div/span[3]').click()
                elif row[1] == '902 POOL FENCE/DOOR ALARM':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[122]/div/span[3]').click()
                elif row[1] == '903 POOL PREFINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[123]/div/span[3]').click()
                elif row[1] == '904 POOL/SPA FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[124]/div/span[3]').click()
                elif row[1] == '925 FURNACE REPLACEMENT':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[125]/div/span[3]').click()
                elif row[1] == '926 ROUGH MECHANICAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[126]/div/span[3]').click()
                elif row[1] == '930 A/C CONDENSER':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[130]/div/span[3]').click()
                elif row[1] == '931 WALL HEATER':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[131]/div/span[3]').click()
                elif row[1] == '932 HVAC PACKAGE UNIT':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[132]/div/span[3]').click()
                elif row[1] == '950 BUILDING FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[133]/div/span[3]').click()
                elif row[1] == '951 ELECTRICAL FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[134]/div/span[3]').click()
                elif row[1] == '952 PLUMBING FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[135]/div/span[3]').click()
                elif row[1] == '953 MECHANICAL FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[136]/div/span[3]').click()
                elif row[1] == '954 GRADING FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[137]/div/span[3]').click()
                elif row[1] == '955 DEMOLITION FINAL':
                        driver.find_element(By.XPATH, '//*[@id="ctl08_treeInspections"]/ul/li[1]/ul/li[138]/div/span[3]').click()

                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_btnSave"]'))
                        ).click()


                driver.switch_to.parent_frame()
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="modalPage"]/div[2]/div/div/table/tbody/tr/td/img[1]'))
                        ).click()
                time.sleep(3)
                WebDriverWait(driver, '45').until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                        )
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.NAME, 'FRMPERMIT'))
                        )
                driver.switch_to.frame("FRMPERMIT")

def transfer(url, driver, permit, permitFileLocation, central_user, central_pass, permtype, permsubtype, needDesc, needFees, needIns, needPR):
    login(url, driver, permit, central_user, central_pass)
    if needPR:
        status = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='ctl09_C_ctl00_lblStatus']"))
                    ).text
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
    if needDesc:
        inputDesc(driver, permit, permitFileLocation, permtype, permsubtype)
    if needFees:
        inputFees(driver, permit, permitFileLocation)
    if needIns:
        inputDesc(driver, permit, permitFileLocation)
    print('program finished')
    return


