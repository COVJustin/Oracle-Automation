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
import shutil
import re
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
def login(url, url2, driver, permit, downloadFileLocation, permitFileLocation, oracle_user, oracle_pass, central_user, central_pass):
    print("logging in to Oracle....")
    driver.get(url2)
    driver.maximize_window()
    
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//oj-menu-button[@id='switchProfileMenu']/button/div"))
            )
    time.sleep(5)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//oj-menu-button[@id='switchProfileMenu']/button/div"))
            ).click()
    time.sleep(1)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Sign In')]"))
            ).click()

    oracleLogin = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='idcs-signin-basic-signin-form-username']"))
            )
    
    oraclePassword = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='idcs-signin-basic-signin-form-password|input']"))
            )

    oracleButton = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//oj-button[@id='idcs-signin-basic-signin-form-submit']/button/div"))
            )
    oracleLogin.send_keys(oracle_user)
    oraclePassword.send_keys(oracle_pass)
    oracleButton.click()

    oracle_search = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='srchListC_input|input']"))
            ) 
    oracle_search.send_keys(permit)
    oracle_search.send_keys(Keys.ENTER)

    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '" + permit + "')]"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(.,'Print Permit')]"))
            )
    print("successfully logged in")

    # Get Basic Permit Info
    time.sleep(1)
    oracleStatus = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicationInformation']/div/div/div/div[2]/span"))
            ).text
    oracleDesc = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='overviewDescription']/div/div/div/div[2]/span"))
            ).text
    if len(oracleDesc) > 46:
        oracleDesc = oracleDesc[:46]
    oracleApplyDate = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicationInformation']/div/div/div/div[6]/div"))
            ).text
    oracleIssDate = ""
    try:
        oracleIssDate += driver.find_element(By.XPATH, "//div[@id='overviewApplicationInformation']/div[2]/div/div/div[2]").text
    except NoSuchElementException:
        print("No date")
    oracleExpDate = ""
    try:
        oracleExpDate += driver.find_element(By.XPATH, "//div[@id='overviewApplicationInformation']/div[2]/div/div[2]/div[2]/span").text
    except NoSuchElementException:
        oracleExpDate = oracleIssDate
        oracleIssDate = ""
        print("No issue date")
    
    # Get Valuation & Type (Not sure how to tackle ATM)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//li[@id='permitDetails']/a/span"))
            ).click()
    #oracleVal = WebDriverWait(driver, '20').until(
    #        EC.presence_of_element_located((By.XPATH, "//input[@id='ccas20_genJobCost']"))
    #        ).text
    #print(oracleVal)
    resvcom = WebDriverWait(driver, '30').until(
            EC.presence_of_element_located((By.XPATH, "//oj-switch[@id='cf-fields112']/input"))
            ).get_attribute('checked')
    oracleType = "RESIDENTIAL"
    if resvcom:
        oracleType = "COMMERCIAL"
    

    # Get Fees
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
            ).click()
    time.sleep(1)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//li[9]/a/span/span"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#PSCLNP_RECORD_DETAIL_of_DEFAULT-feeRecord-feeItem-Download-DownloadButton .psc-sui-icon-placeholder"))
            ).click()
    time.sleep(7.5)
    shutil.move(downloadFileLocation + '/Fees and Payments.csv', permitFileLocation + "/" + permit + ' Fees.csv')

    # Get Inspections
    skipInspec = False
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//div/ul/li[7]/a/span/span"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#ice_inspection_list-Download-DownloadButton .psc-sui-icon-placeholder"))
            ).click()
    time.sleep(7.5)
    try:
        driver.find_element(By.XPATH, "//button[@id='ojAlertDialogOKBtn-0']/div/span").click()
        time.sleep(2)
        skipInspec = True
    except NoSuchElementException:
        shutil.move(downloadFileLocation + '/Inspection.csv', permitFileLocation + "/" + permit + ' Inspection.csv')

    # Get Reviews
    skipRev = False
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//li[6]/ul/li[2]/a/span"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='addPlanReview']"))
            )
    time.sleep(5)
    try:
        cycleCount = driver.find_element(By.XPATH, "//label[@id='HeaderPlanReviewCycleHeaderLabel|label']").text
        df = pd.DataFrame(columns=["date1", "revtype", "reviewer", "date2", "result", "date3", "notes"])
        cycleCount = int(cycleCount[-1])
        cycleTracker = cycleCount
        commentDic = {}
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//a[@id='prViewPlanCommentsLinkLeft']/span"))
                ).click()
        try:
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(1) .oj-flex-item .oj-flex-item:nth-child(1)")
            commentCount = WebDriverWait(driver, '20').until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "psc-lnp-review-panel"))
                        )
            for i in range(len(commentCount)):
                commentCycleNum = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") .oj-flex-item .oj-flex-item:nth-child(1)"))
                        ).text[-1]
                commentRevAndType = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") .oj-flex-item .oj-flex-item:nth-child(2)"))
                        ).text.split(" | ")
                commentRev = commentRevAndType[0]
                commentType = commentRevAndType[1]
                commentText = ""
                commentTextList = WebDriverWait(driver, '20').until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") p, .psc-lnp-review-panel:nth-child(" + str(i + 1) + ") li"))
                        )
                for x in commentTextList:
                    commentText += x.text
                commentDic[commentCycleNum + commentRev + commentType] = commentText
        except NoSuchElementException:
            print("no comments")
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='planReviewViewCommentsModal']/div/button/div"))
                ).click()
        if cycleCount != 1:
            for i in range(cycleCount):
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[@id='prChangeCycleLink']/span"))
                        ).click()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//tr[" + str(cycleTracker) + "]/td[8]/div/td/button/div/span"))
                        ).click()
                body = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//div[3]/div/oj-table/table/tbody"))
                        )
                rowCount = WebDriverWait(body, '20').until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
                        )
                header = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//label[@id='HeaderPlanReviewOpenByInfoLff|label']"))
                        ).text
                date1 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', header)[0]
                for j in range(len(rowCount)):
                    reviewer = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerNameUserTable" + str(j) + "']"))
                        ).text
                    if reviewer == "Solano Environmental Health":
                        revtype = "Solano Co-Environmental Health"
                    else:
                        revtype = WebDriverWait(driver, '20').until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#prDepartmentUserTable_" + str(j) +" > span"))
                            ).text
                    date2 = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerDueDateUserTable_" + str(j) + "']"))
                        ).text
                    result = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionStatusUserTable3_" + str(j) + "']"))
                        ).text
                    date3temp = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionDttmUserTable_" + str(j) + "']"))
                        ).text
                    date3 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', date3temp)[0]
                    notes = ""
                    tempCheck = str(i + 1) + reviewer + revtype
                    if tempCheck in commentDic:
                        notes += commentDic[tempCheck]
                    df2 = pd.DataFrame([[date1, revtype, reviewer, date2, result, date3, notes]],columns=["date1", "revtype", "reviewer", "date2", "result", "date3", "notes"])
                    df = df.append(df2,ignore_index=True)
                cycleTracker -= 1
        else:
            body = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//div[3]/div/oj-table/table/tbody"))
                    )
            rowCount = WebDriverWait(body, '20').until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
                    )
            header = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//label[@id='HeaderPlanReviewOpenByInfoLff|label']"))
                    ).text
            date1 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', header)[0]
            for j in range(len(rowCount)):
                revtype = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#prDepartmentUserTable_" + str(j) +" > span"))
                    ).text
                reviewer = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerNameUserTable" + str(j) + "']"))
                    ).text
                date2 = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerDueDateUserTable_" + str(j) + "']"))
                    ).text
                result = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionStatusUserTable3_" + str(j) + "']"))
                    ).text
                date3temp = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionDttmUserTable_" + str(j) + "']"))
                    ).text
                date3 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', date3temp)[0]
                notes = ""
                tempCheck = str(1) + reviewer + revtype
                if tempCheck in commentDic:
                    notes += commentDic[tempCheck]
                df2 = pd.DataFrame([[date1, revtype, reviewer, date2, result, date3, notes]],columns=["date1", "revtype", "reviewer", "date2", "result", "date3", "notes"])
                df = df.append(df2,ignore_index=True)
        df.to_csv(permitFileLocation + "/" + permit + " Reviews.csv", index=False, header=False)
    except NoSuchElementException:
        skipRev = True

    print("logging in to Central Square....")
    driver.execute_script("window.open('https://www.google.com/', 'new_window')")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    
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

    print("successfully logged in")

    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
    driver.switch_to.frame("FRMPERMIT")   

    # Permit Info
    statusDic = {
        "Approved": "APPROVED",
        "Expired": "EXPIRED",
        "Inspection": "ISSUED",
        "Plan Review": "PLAN CHECK",
        "Submitted": "APPLIED"
    }

    status = statusDic[oracleStatus]

    desc = oracleDesc + " " + permit
    applyDate = oracleApplyDate
    expDate = oracleExpDate
    issueDate = oracleIssDate

    permType = oracleType
    valuation = "20,650.00"
    
    # Change Reviews (Check for Public Works equivalent)
    reviewDic = {
        "Planning": "]/ul/li[12]/div/span[3]",
        "Building": "]/ul/li[3]/div/span[3]",
        "Water": "]/ul/li[22]/div/span[3]",
        "Flood Wastewater": "]/ul/li[30]/div/span[3]",
        "Fire": "]/ul/li[29]/div/span[3]",
        "Public Works-Flood Zone": "]/ul/li[19]/div/span[3]",
        "Public Works-Current Dev": "]/ul/li[16]/div/span[3]",
        "Public Works-Waste Mgmt": "]/ul/li[21]/div/span[3]",
        "Public Works-Traffic": "]/ul/li[20]/div/span[3]",
        "Public Works": "]/ul/li[16]/div/span[3]",
        "Solano Co-Environmental Health": "]/ul/li[24]/div/span[3]"
    }
    reviewStatusDic = {
        "Approved": "APPROVED",
        "Revision Required": "PLAN REVIEW CORRECTIONS",
        "Not Required": "REVIEW NOT REQUIRED",
        "Rejected": "DENIED",
        "Canceled": "WITHDRAWN"
    }

    if skipRev == False:
        with open("Oracle-Automation/Permits/" + permit + " Reviews.csv", "r", newline='', encoding='utf8') as file:
            reader2 = csv.reader(file)
            reviewData = list(reader2)
        cycleCounter = 0
        editCounter = 0
        dateTrack = dt.strptime("1/1/01", "%m/%d/%y")
        for i in range(0, len(reviewData)):
            if reviewData[i][1] in reviewDic:
                try:
                    WebDriverWait(driver, '20').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                            ).click()
                except ElementClickInterceptedException:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(2)
                    WebDriverWait(driver, '20').until(
                            EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_btnAddReview']"))
                            ).click()
                driver.switch_to.parent_frame()
                innerframe = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(innerframe)
                currDate = dt.strptime(reviewData[i][0], "%m/%d/%y")
                if currDate > dateTrack:
                    cycleCounter += 1
                    dateTrack = currDate
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//div/ul/li[" + str(eval('3 + ' + str(cycleCounter))) + "]/div/span[2]"))
                        ).click()
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[" + str(eval('3 + ' + str(cycleCounter))) + reviewDic[reviewData[i][1]]))
                        ).click()
                time.sleep(2)
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_ddContactName_Input']"))
                        ).click()
                try:
                    time.sleep(2.5)
                    driver.find_element(By.XPATH, "//li[contains(.,'" + reviewData[i][2].upper() + "')]").click()
                except NoSuchElementException:
                    WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[@id='ctl08_ddContactName_Arrow']"))
                        ).click()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_ddStatus_Input']"))
                        ).click()
                time.sleep(1)
                WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'" + reviewStatusDic[reviewData[i][4]] + "')]"))
                        ).click()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calSentDate_dateInput']"))
                        )
                sentDateField = driver.find_element(By.XPATH, "//input[@id='ctl08_calSentDate_dateInput']")
                sentDateField.send_keys(Keys.CONTROL + "a")
                sentDateField.send_keys(Keys.DELETE)
                sentDateField.send_keys(reviewData[i][0])
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calDueDate_dateInput']"))
                        )
                dueDateField = driver.find_element(By.XPATH, "//input[@id='ctl08_calDueDate_dateInput']")
                dueDateField.send_keys(Keys.CONTROL + "a")
                dueDateField.send_keys(Keys.DELETE)
                dueDateField.send_keys(reviewData[i][3])
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_txtRemarks']"))
                        )
                remarks = driver.find_element(By.XPATH, "//input[@id='ctl08_txtRemarks']")
                remarks.send_keys("transferred from oracle (program)")
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[@id='ctl08_txtNote']"))
                        )
                note = driver.find_element(By.XPATH, "//textarea[@id='ctl08_txtNote']")
                note.send_keys(reviewData[i][6])
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                        ).click()
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)"))
                        ).click()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                        )
                driver.switch_to.frame("FRMPERMIT")
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl15_C_ctl00_rlvReviews_ctrl" + str(editCounter) + "_btnEdit']"))
                        ).click()
                editCounter += 1
                driver.switch_to.parent_frame()
                innerframe2 = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.NAME, 'rw'))
                        )
                driver.switch_to.frame(innerframe2)
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_calReceivedDate_dateInput']"))
                        )
                recDate = driver.find_element(By.XPATH, "//input[@id='ctl08_calReceivedDate_dateInput']")
                recDate.send_keys(Keys.CONTROL + "a")
                recDate.send_keys(Keys.DELETE)
                recDate.send_keys(reviewData[i][5])
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='ctl08_btnSave']"))
                        ).click()
                time.sleep(5)
                driver.switch_to.parent_frame()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                        )
                driver.switch_to.frame("FRMPERMIT")

    # Click edit
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)
    WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ctl09_C_ctl00_btnEdit']"))
            ).click()

    # Change Status
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
            ).click()
    time.sleep(1)
    WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ status +"')]"))
            ).click()
    
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
        WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='btnClose']"))
            ).click()
        driver.switch_to.parent_frame()
    except NoSuchElementException:
        print("Valid expiration")
    WebDriverWait(driver, '20').until(
        EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
        )
    driver.switch_to.frame("FRMPERMIT")
    time.sleep(5)
    WebDriverWait(driver, '20').until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
            )
    """
    # Change Valuation
    try:
        time.sleep(5)
        driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnEditAllValuationsBottom']").click()
    except NoSuchElementException:
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$btnAddValuation']"))
                ).click()
        driver.switch_to.parent_frame()
        innerframe4 = WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.NAME, 'rw'))
                )
        time.sleep(5)
        driver.switch_to.frame(innerframe4)
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//strong[contains(.,'JOB VALUATION = $1.00/EA')]"))
                ).click()
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                ).click()
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
    valField = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$rGridValuations$ctl00$ctl04$txtParentQty']"))
            )
    valField.send_keys(valuation)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnSaveAllValuationsTop']"))
            ).click()
    """
    
    # Change Fees (Needs Optimization)
    feeDic = {
        "Plan Check Fee": "BLG-PLAN REVIEW FEE",
        "Building Permit Fee": "BLG-BUILDING PERMIT",
        "Title 24 Fee": "BLG-TITLE 24 ENERGY CONSERVATION REVIEW",
        "Disable Access Review": "BLG-DISABLE ACCESS REVIEW",
        "State SMIP Fee": "STATE-SMIP RESIDENTIAL",
        "Mechanical Permit Fee": "BLG-MECHANICAL PERMIT",
        "Electrical Permit Fee": "BLG-ELECTRICAL PERMIT",
        "General Plan Update Surcharge": "GENERAL PLAN UPDATE SURCHARGE",
        "Permit Streamlining Surcharge": "PERMIT STREAMLINING SURCHARGE",
        "Surcharge - Building Technology Fee": "TECHNOLOGY SURCHARGE FEE",
        "Surcharge - Engineering Technology Fee": "TECHNOLOGY SURCHARGE FEE",
        "Surcharge - Planning Technology Fee": "TECHNOLOGY SURCHARGE FEE",
        "State Building Standards Fee - Admin Surcharge": "STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE",
        "State Building Standards Fee": "STATE-BUILDING STANDARDS FEE",
        "CAL Green Building Standards Review": "BLG-CALGREEN BULDING STANDARDS REVIEW",
        "Fire Site Plan Review": "SITE PLAN REVIEW",
        "Assistant Civil Engineer Review/Inspection": "ASSISTANT CIVIL ENGINEER",
        "C1 PW Waste Management Plan": "C1 GEN FD WASTE MGMT PLAN-BLG",
        "C1, C2, C3 Permit Coordination Fees": "C1 PERMIT COORDINATION FEE",
        "C3 SW Cost Constr. & Demo Recycling": "C3 SW COST CONSTR & DEMO RECYCLING",
        "C2 SW Fee Constr. & Demo Recycling": "C2 SW FEE CONSTR & DEMO RECYCLING",
        "Plumbing Permit Fee": "BLG-PLUMBING PERMIT",
        "Associate Civil Engineer Review/Inspection": "ASSOCIATE CIVIL ENGINEER",
        "Planning Over-the-Counter Permit Review Fee": "OVER THE COUNTER PERMIT REVIEW APPLICATION FEE",
        "Plan Re-Issuance Fee": "PLAN RE-ISSUANCE FEE - DOES NOT INCLUDE COPY COST",
        "Consultant Review/Inspection": "CONSULTANT REVIEW AND/OR INSPECTION",
        "Senior Engineering Technician Review/Inspection": "SENIOR ENGINEERING TECHNICIAN",
        "Engineering Technician Review/Inspection": "ENGINEERING TECH II",
        "Planning Non-Entitlement Permit Review Fee": "NON-ENTITLEMENT PERMIT REVIEW APPLICATION FEE",
        "Senior Civil Engineer Review/Inspection": "SENIOR CIVIL ENGINEER",
        "Encroachment Working w/o a Permit": "BUILDING PERMIT PENALTY",
        "Excavation Working w/o a Permit": "BUILDING PERMIT PENALTY",
        "County Facilities Impact - Multi-Family Age Restr.": "COUNTY FACILITIES-MULTI-FAMILY AGE RESTRICTED",
        "County Facilities Impact - Second Unit": "COUNTY FACILITIES-SECOND UNIT",
        "School Impact - Residential Additions/ADUs": "SCHOOL FEE-RESIDENTIAL ADDITIONS >500 SF",
        "Columbus Parkway Impact Payment": "DEV IMPACT-COLUMBUS PKWY PAYMENT",
        "County Facilities Impact - Health Care Facility": "COUNTY FACILITIES-HEALTH CARE FACILITY",
        "County Facilities Impact - Place of Worship": "COUNTY FACILITIES-PLACE OF WORSHIP",
        "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Excise": "HB. I-80 OVERPASS FUND 211 EXCISE TAX",
        "Transportation Impact - Commercial": "TRANSPORTATION-COMMERCIAL",
        "Northgate District 94-1 Impact - Retail": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT",
        "County Facilities Impact - Congregate Care Fac.": "COUNTY FACILITIES-CONGREGATE CARE FACILITY",
        "County Facilities Impact - Service Commercial": "COUNTY FACILITIES-SERVICE COMMERCIAL",
        "County Facilities Impact - Single Family": "COUNTY FACILITIES-SINGLE FAMILY",
        "Excise Tax - Commercial and Offices": "EXCISE TAX- COMMERCIAL & OFFICES",
        "GVRD Park Impact - Single Fam Attached per Unit": "GVRD SINGLE FAMILY ATTACHED/UNIT",
        "Hiddenbr./I-80 Impact - Gen Fund 001 Excise Tax": "HB. I-80 GENERAL FUND 001 EXCISE TAX",
        "School Impact - Commercial & Offices New/Addition": "SCHOOL FEE-COMMERCIAL & OFFICES",
        "Transportation Impact - Motels, Hotels": "TRANSPORTATION-MOTELS/HOTELS",
        "Northgate District 94-1 Impact - Multi-Family": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT",
        "County Facilities Impact - Assembly Uses": "COUNTY FACILITIES-ASSEMBLY USES",
        "County Facilities Impact - Private School": "COUNTY FACILITIES-PRIVATE SCHOOL",
        "County Facilities Impact - Retail": "COUNTY FACILITIES-RETAIL",
        "Excise Tax - Residential": "EXCISE TAX- RESIDENTIAL",
        "GVRD Park Impact - Multi-Family per Unit": "GVRD MULTI FAMILY/UNIT",
        "GVRD Park Impact - Mobile Home per Unit": "GVRD MOBILE HOME/UNIT",
        "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Surcharge": "HB. I-80 OVERPASS FUND 211 SURCHARGE",
        "Transportation Impact - Multi-Family": "TRANSPORTATION-MULTI-FAMILY",
        "Improvement Permit Inspection Consultant": "CONSULTANT REVIEW AND/OR INSPECTION",
        "County Facilities Impact - Hotel, Motel": "COUNTY FACILITIES-HOTEL/MOTEL",
        "County Facilities Impact - Child Day Care Facility": "COUNTY FACILITIES-CHILD DAY CARE FACILITY",
        "County Facilities Impact - Warehouse": "COUNTY FACILITIES-WAREHOUSE",
        "County Facilities Impact - Barn": "COUNTY FACILITIES-BARN",
        "County Facilities Impact - Multi-Family": "COUNTY FACILITIES-MULTI-FAMILY",
        "County Facilities Impact - Industrial": "COUNTY FACILITIES-INDUSTRIAL",
        "County Facilities Impact - Office": "COUNTY FACILITIES-OFFICE",
        "GVRD Park Impact - Duplex per Unit": "GVRD DUPLEX/UNIT",
        "GVRD Park Impact - Single Fam Detached per Unit": "GVRD SINGLE FAMILY DETACHED/UNIT",
        "Transportation Impact - Industrial": "TRANSPORTATION-INDUSTRIAL",
        "Sky Valley Improvement District Impact": "DEV IMPACT-SKY VALLEY IMPROVEMENT DIST",
        "Duplicate Permit Card Fee": "BLG-DUPLICATE PERMIT CARD",
        "Building Permit/Plan Check Extension Request": "PLAN CHECK EXTENSION REQUEST REVIEW FEE",
        "Administrative Citation 1": "BLG-ADMINISTRATIVE CITATION-1",
        "Northgate District 94-1 Impact - Single Family": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT",
        "Northgate District 94-1 Impact - Business Office": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT",
        "Penalty Fee for Work Done w/o Permit": "BUILDING PERMIT PENALTY",
        "Permit Application Fee": "APPLICATION PROCESSING FEE"
    }

    with open("Oracle-Automation/Permits/" + permit + " Fees.csv", "r", newline='') as f:
        reader = csv.reader(f)
        tempData = list(reader)
    tempData.pop(0)
    data = [x for x in tempData if (x[3] == "PAID" or x[3] == "DUE")]

    transferred = [False] * len(data)
    while False in transferred:
        WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
            )
        WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
            ).click()
        driver.switch_to.parent_frame()
        innerframe5 = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.NAME, 'rw'))
            )
        driver.switch_to.frame(innerframe5)
        time.sleep(5)
        WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
            )
        WebDriverWait(driver, '20').until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl08_imgBtnCancel']"))
            )
        check1 = 0
        check2 = 0
        check3 = 0
        check4 = 0
        check5 = 0
        check6 = 0
        check7 = 0
        check8 = 0
        check9 = 0
        check10 = 0
        check11 = 0
        check12 = 0
        check13 = 0
        check14 = 0
        check15 = 0
        check16 = 0
        check17 = 0
        check18 = 0
        check19 = 0
        check20 = 0
        check21 = 0
        check22 = 0
        check23 = 0
        check24 = 0
        check25 = 0
        check26 = 0
        check27 = 0
        check28 = 0
        check29 = 0
        check30 = 0
        check31 = 0
        check32 = 0
        check33 = 0
        check34 = 0
        check35 = 0
        check36 = 0
        check37 = 0
        check38 = 0
        check39 = 0
        check40 = 0
        check41 = 0
        check42 = 0
        check43 = 0
        check44 = 0
        check45 = 0
        check46 = 0
        check47 = 0
        check48 = 0
        check49 = 0
        check50 = 0
        check51 = 0
        check52 = 0
        check53 = 0
        check54 = 0
        check55 = 0
        check56 = 0
        check57 = 0
        check58 = 0
        check59 = 0
        check60 = 0
        check61 = 0
        check62 = 0
        check63 = 0
        check64 = 0
        check65 = 0
        check66 = 0
        check67 = 0
        check68 = 0
        check69 = 0
        check70 = 0
        check71 = 0
        for i in range(0, len(data)):
            if (data[i][3] == "PAID" or data[i][3] == "DUE") and transferred[i] == False:
                if data[i][0] == "Plan Check Fee" and check1 == 0:
                    check1 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-PLAN REVIEW FEE = .7*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "Building Permit Fee" and check2 == 0:
                    check2 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-BUILDING PERMIT = [1ABUILDPERM22-23]')]"))
                        ).click()
                elif data[i][0] == "Title 24 Fee" and check3 == 0:
                    check3 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-TITLE 24 ENERGY CONSERVATION REVIEW = .1*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "Disable Access Review" and check4 == 0:
                    check4 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-DISABLE ACCESS REVIEW = .15*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "State SMIP Fee" and check5 == 0:
                    check5 += 1
                    transferred[i] = True
                    if permType == "RESIDENTIAL":
                        WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'STATE-SMIP RESIDENTIAL = (MAX((JOBVALUE*.00013), .5))')]"))
                        ).click()
                    else:
                        feeDic["State SMIP Fee"] = "STATE-SMIP COMMERCIAL"
                        WebDriverWait(driver, '20').until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'STATE-SMIP COMMERCIAL = (MAX((JOBVALUE*.00028), .5))')]"))
                            ).click()
                elif data[i][0] == "Mechanical Permit Fee" and check6 == 0:
                    check6 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-MECHANICAL PERMIT = .25*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "Electrical Permit Fee" and check7 == 0:
                    check7 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-ELECTRICAL PERMIT = .2*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "General Plan Update Surcharge" and check8 == 0:
                    check8 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GENERAL PLAN UPDATE SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.05)')]"))
                        ).click()
                elif data[i][0] == "Permit Streamlining Surcharge" and check9 == 0:
                    check9 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'PERMIT STREAMLINING SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.03)')]"))
                        ).click()
                elif (data[i][0] == "Surcharge - Building Technology Fee" or data[i][0] == "Surcharge - Engineering Technology Fee" or data[i][0] == "Surcharge - Planning Technology Fee") and check10 == 0:
                    check10 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)')]"))
                        ).click()
                elif data[i][0] == "State Building Standards Fee - Admin Surcharge" and check11 == 0:
                    check11 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE = .10*[STBSTDS]')]"))
                        ).click()
                elif data[i][0] == "State Building Standards Fee" and check12 == 0:
                    check12 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'STATE-BUILDING STANDARDS FEE = .90*[STBSTDS]')]"))
                        ).click()
                elif data[i][0] == "CAL Green Building Standards Review" and check13 == 0:
                    check13 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-CALGREEN BULDING STANDARDS REVIEW = .1*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "Fire Site Plan Review" and check14 == 0:
                    check14 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'SITE PLAN REVIEW = [FIRESITEPLAN2022]')]"))
                        ).click()
                elif data[i][0] == "Assistant Civil Engineer Review/Inspection" and check15 == 0:
                    check15 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'ASSISTANT CIVIL ENGINEER = QTY*130')]"))
                        ).click()
                elif data[i][0] == "C1 PW Waste Management Plan" and check16 == 0:
                    check16 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C1 GEN FD WASTE MGMT PLAN-BLG = 453')]"))
                        ).click()
                elif data[i][0] == "C1, C2, C3 Permit Coordination Fees" and check17 == 0:
                    check17 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C1 PERMIT COORDINATION FEE = 14')]"))
                        ).click()
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C2 PERMIT COORDINATION FEE = 2')]"))
                        ).click()
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C3 PERMIT COORDINATION FEE = 1')]"))
                        ).click()
                elif data[i][0] == "C3 SW Cost Constr. & Demo Recycling" and check18 == 0:
                    check18 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C3 SW COST CONSTR & DEMO RECYCLING = 8')]"))
                        ).click()
                elif data[i][0] == "C2 SW Fee Constr. & Demo Recycling" and check19 == 0:
                    check19 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'C2 SW FEE CONSTR & DEMO RECYCLING = 94')]"))
                        ).click()
                elif data[i][0] == "Plumbing Permit Fee" and check20 == 0:
                    check20 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-PLUMBING PERMIT = .3*{BLDG}')]"))
                        ).click()
                elif data[i][0] == "Associate Civil Engineer Review/Inspection" and check21 == 0:
                    check21 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'ASSOCIATE CIVIL ENGINEER = QTY*147')]"))
                        ).click()
                elif data[i][0] == "Planning Over-the-Counter Permit Review Fee" and check22 == 0:
                    check22 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'OVER THE COUNTER PERMIT REVIEW APPLICATION FEE = 56')]"))
                        ).click()
                elif data[i][0] == "Plan Re-Issuance Fee" and check23 == 0:
                    check23 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'PLAN RE-ISSUANCE FEE - DOES NOT INCLUDE COPY COST = 89')]"))
                        ).click()
                elif data[i][0] == "Consultant Review/Inspection" and check24 == 0:
                    check24 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'CONSULTANT REVIEW AND/OR INSPECTION = QTY *1.2')]"))
                        ).click()
                elif data[i][0] == "Senior Engineering Technician Review/Inspection" and check25 == 0:
                    check25 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'SENIOR ENGINEERING TECHNICIAN = QTY*138')]"))
                        ).click()
                elif data[i][0] == "Engineering Technician Review/Inspection" and check26 == 0:
                    check26 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'ENGINEERING TECH II = QTY*124')]"))
                        ).click()
                elif data[i][0] == "Planning Non-Entitlement Permit Review Fee" and check27 == 0:
                    check27 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'NON-ENTITLEMENT PERMIT REVIEW APPLICATION FEE = 215')]"))
                        ).click()
                elif data[i][0] == "Senior Civil Engineer Review/Inspection" and check28 == 0:
                    check28 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'SENIOR CIVIL ENGINEER = QTY*164')]"))
                        ).click()
                elif (data[i][0] == "Encroachment Working w/o a Permit" or data[i][0] == "Excavation Working w/o a Permit" or data[i][0] == "Penalty Fee for Work Done w/o Permit") and check29 == 0:
                    check29 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BUILDING PERMIT PENALTY = 2 X ORIG PMT')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Multi-Family Age Restr." and check30 == 0:
                    check30 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-MULTI-FAMILY AGE RESTRICTED = QTY*3975')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Second Unit" and check31 == 0:
                    check31 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-SECOND UNIT = QTY* 4536')]"))
                        ).click()
                elif data[i][0] == "School Impact - Residential Additions/ADUs" and check32 == 0:
                    check32 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'SCHOOL FEE-RESIDENTIAL ADDITIONS >500 SF = QTY*2.24')]"))
                        ).click()
                elif data[i][0] == "Columbus Parkway Impact Payment" and check33 == 0:
                    check33 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'DEV IMPACT-COLUMBUS PKWY PAYMENT = 15432.81')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Health Care Facility" and check34 == 0:
                    check34 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-HEALTH CARE FACILITY = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Place of Worship" and check35 == 0:
                    check35 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-PLACE OF WORSHIP = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Excise" and check36 == 0:
                    check36 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'HB. I-80 OVERPASS FUND 211 EXCISE TAX = 4021')]"))
                        ).click()
                elif data[i][0] == "Transportation Impact - Commercial" and check37 == 0:
                    check37 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'TRANSPORTATION-COMMERCIAL = 4 * QTY')]"))
                        ).click()
                elif (data[i][0] == "Northgate District 94-1 Impact - Retail" or data[i][0] == "Northgate District 94-1 Impact - Multi-Family" or data[i][0] == "Northgate District 94-1 Impact - Single Family" or data[i][0] == "Northgate District 94-1 Impact - Business Office") and check38 == 0:
                    check38 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT = 3398')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Congregate Care Fac." and check39 == 0:
                    check39 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-CONGREGATE CARE FACILITY = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Service Commercial" and check40 == 0:
                    check40 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-SERVICE COMMERCIAL = QTY*2097/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Single Family" and check41 == 0:
                    check41 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-SINGLE FAMILY = QTY* 9263')]"))
                        ).click()
                elif data[i][0] == "Excise Tax - Commercial and Offices" and check42 == 0:
                    check42 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'EXCISE TAX- COMMERCIAL & OFFICES = QTY*.47')]"))
                        ).click()
                elif data[i][0] == "GVRD Park Impact - Single Fam Attached per Unit" and check43 == 0:
                    check43 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GVRD SINGLE FAMILY ATTACHED/UNIT = QTY*12907')]"))
                        ).click()
                elif data[i][0] == "Hiddenbr./I-80 Impact - Gen Fund 001 Excise Tax" and check44 == 0:
                    check44 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'HB. I-80 GENERAL FUND 001 EXCISE TAX = 1000')]"))
                        ).click()
                elif data[i][0] == "School Impact - Commercial & Offices New/Addition" and check45 == 0:
                    check45 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'SCHOOL FEE-COMMERCIAL & OFFICES = QTY*.36')]"))
                        ).click()
                elif data[i][0] == "Transportation Impact - Motels, Hotels" and check46 == 0:
                    check46 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'TRANSPORTATION-MOTELS/HOTELS = QTY * 4768.23')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Riding Arena" and check47 == 0:
                    check47 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-RIDING ARENA = QTY*174/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Assembly Uses" and check48 == 0:
                    check48 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-ASSEMBLY USES = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Private School" and check49 == 0:
                    check49 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-PRIVATE SCHOOL = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Retail" and check50 == 0:
                    check50 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-RETAIL = QTY* 1024/1000')]"))
                        ).click()
                elif data[i][0] == "Excise Tax - Residential" and check51 == 0:
                    check51 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'EXCISE TAX- RESIDENTIAL = (MAX(QTY,1)) * 5613')]"))
                        ).click()
                elif data[i][0] == "GVRD Park Impact - Multi-Family per Unit" and check52 == 0:
                    check52 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GVRD MULTI FAMILY/UNIT = QTY*9808')]"))
                        ).click()
                elif data[i][0] == "GVRD Park Impact - Mobile Home per Unit" and check53 == 0:
                    check53 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GVRD MOBILE HOME/UNIT = QTY*8588')]"))
                        ).click()
                elif data[i][0] == "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Surcharge" and check54 == 0:
                    check54 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'HB. I-80 OVERPASS FUND 211 SURCHARGE = 979')]"))
                        ).click()
                elif data[i][0] == "Transportation Impact - Multi-Family" and check55 == 0:
                    check55 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'TRANSPORTATION-MULTI-FAMILY = QTY * 4768.23')]"))
                        ).click()
                elif data[i][0] == "Improvement Permit Inspection Consultant" and check56 == 0:
                    check56 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'CONSULTANT REVIEW AND/OR INSPECTION = QTY *1.2')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Hotel, Motel" and check57 == 0:
                    check57 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-HOTEL/MOTEL = QTY*429/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Child Day Care Facility" and check58 == 0:
                    check58 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-CHILD DAY CARE FACILITY = QTY*483/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Warehouse" and check59 == 0:
                    check59 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-WAREHOUSE = QTY*210/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Barn" and check60 == 0:
                    check60 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-BARN = QTY*174/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Multi-Family" and check61 == 0:
                    check61 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-MULTI-FAMILY = QTY * 6662')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Industrial" and check62 == 0:
                    check62 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-INDUSTRIAL = QTY * 698/1000')]"))
                        ).click()
                elif data[i][0] == "County Facilities Impact - Office" and check63 == 0:
                    check63 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'COUNTY FACILITIES-OFFICE = QTY * 1359/1000')]"))
                        ).click()
                elif data[i][0] == "GVRD Park Impact - Duplex per Unit" and check64 == 0:
                    check64 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GVRD DUPLEX/UNIT = QTY*11686')]"))
                        ).click()
                elif data[i][0] == "GVRD Park Impact - Single Fam Detached per Unit" and check65 == 0:
                    check65 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'GVRD SINGLE FAMILY DETACHED/UNIT = QTY*14315')]"))
                        ).click()
                elif data[i][0] == "Transportation Impact - Industrial" and check66 == 0:
                    check66 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'TRANSPORTATION-INDUSTRIAL = 1.99 * QTY')]"))
                        ).click()
                elif data[i][0] == "Sky Valley Improvement District Impact" and check67 == 0:
                    check67 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'DEV IMPACT-SKY VALLEY IMPROVEMENT DIST = 1947')]"))
                        ).click()
                elif data[i][0] == "Duplicate Permit Card Fee" and check68 == 0:
                    check68 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-DUPLICATE PERMIT CARD = 20')]"))
                        ).click()
                elif data[i][0] == "Building Permit/Plan Check Extension Request" and check69 == 0:
                    check69 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'PLAN CHECK EXTENSION REQUEST REVIEW FEE = 89')]"))
                        ).click()
                elif data[i][0] == "Administrative Citation 1" and check70 == 0:
                    check70 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'BLG-ADMINISTRATIVE CITATION-1 = 267')]"))
                        ).click()
                elif data[i][0] == "Permit Application Fee" and check71 == 0:
                    check71 += 1
                    transferred[i] = True
                    WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'APPLICATION PROCESSING FEE = 32')]"))
                        ).click()
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
                ).click()
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '20').until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@class='TelerikModalOverlay']"))
                )
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '20').until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                )
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
                )
        driver.switch_to.frame("FRMPERMIT")
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnCancelEditAllFeesBottom']"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnEditAllFeesBottom']"))
            )
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)
    driver.find_element(By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnEditAllFeesBottom']").click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
            )

    # Needs Potential Optimizing
    for i in range(0, len(data)):
        if (data[i][3] == "PAID" or data[i][3] == "DUE"):
            keywrds = [feeDic[item[0]] for item in data]
            if feeDic[data[i][0]] == "STATE-BUILDING STANDARDS FEE" or feeDic[data[i][0]] == "STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE":
                print("skipped")
            elif feeDic[data[i][0]] == "C1 PERMIT COORDINATION FEE":
                coordType1 = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[text()='" + feeDic[data[i][0]] +"']"))
                        )
                coordRow1 = coordType1.find_element(By.XPATH, "..")
                coordRow2 = coordRow1.find_element(By.XPATH, "..")
                coordInput1 = WebDriverWait(coordRow2, '20').until(
                        EC.presence_of_element_located((By.XPATH, ".//input[contains(@id,'FeeAmount')]"))
                        )
                coordInput1.send_keys(Keys.CONTROL + "a")
                coordInput1.send_keys(Keys.DELETE)
                coordInput1.send_keys(data[i][1])
                coordType2 = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[text()='C2 PERMIT COORDINATION FEE']"))
                        )
                coordRow3 = coordType2.find_element(By.XPATH, "..")
                coordRow4 = coordRow3.find_element(By.XPATH, "..")
                coordInput2 = WebDriverWait(coordRow4, '20').until(
                        EC.presence_of_element_located((By.XPATH, ".//input[contains(@id,'FeeAmount')]"))
                        )
                coordInput2.send_keys(Keys.CONTROL + "a")
                coordInput2.send_keys(Keys.DELETE)
                coordInput2.send_keys("0")
                coordType3 = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[text()='C3 PERMIT COORDINATION FEE']"))
                        )
                coordRow5 = coordType3.find_element(By.XPATH, "..")
                coordRow6 = coordRow5.find_element(By.XPATH, "..")
                coordInput3 = WebDriverWait(coordRow6, '20').until(
                        EC.presence_of_element_located((By.XPATH, ".//input[contains(@id,'FeeAmount')]"))
                        )
                coordInput3.send_keys(Keys.CONTROL + "a")
                coordInput3.send_keys(Keys.DELETE)
                coordInput3.send_keys("0")
            elif keywrds.count(feeDic[data[i][0]]) > 1:
                dupes = {value : [j for j, v in enumerate(keywrds) if value == v] for value in set(keywrds)}
                listofSiblings = driver.find_elements(By.XPATH, "//a[text()='" + feeDic[data[i][0]] +"']")
                tempDic = {}
                count = 0
                for h in listofSiblings:
                    tempDic[dupes[feeDic[data[i][0]]][count]] = h.get_attribute('id')
                    count += 1
                siblingType = WebDriverWait(driver, '20').until(
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

            else:
                feeType = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//a[text()='" + feeDic[data[i][0]] +"']"))
                        )
                row = feeType.find_element(By.XPATH, "..")
                row2 = row.find_element(By.XPATH, "..")
                feeInput = WebDriverWait(row2, '20').until(
                        EC.presence_of_element_located((By.XPATH, ".//input[contains(@id,'FeeAmount')]"))
                        )
                feeInput.send_keys(Keys.CONTROL + "a")
                feeInput.send_keys(Keys.DELETE)
                feeInput.send_keys(data[i][1])
    driver.switch_to.parent_frame()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1) > img:nth-child(1)"))
            ).click()
    WebDriverWait(driver, '20').until(
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
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
            ).click()
    driver.switch_to.frame("FRMPERMIT")
    
    inspectDict = {
        "101 Survey/Set Backs": "101-SURVEY/SET BACKS",
        "102 Ufer/Ground Electrode": "102-UFER/GRND. ELECTRODE",
        "103 Piers": "103-PIERS",
        "104 Footings": "104-FOOTINGS",
        "105 Slab Foundations": "105-SLAB FOUNDATIONS",
        "106 Slab Garage": "106-SLAB GARAGE",
        "107 Driveway": "107-DRIVEWAY",
        "108 Demolition": "108-DEMOLITION",
        "200 Rough Grading": "200-ROUGH GRADING",
        "201 Finish Grading": "200-FINISH GRADING",
        "202 Gen Bldg Site/In-Pro": "202-GEN BLDG SITE/IN-PRO",
        "300 MH Set-Up": "300-MH SET-UP",
        "301 MH Accessory Insp": "301-MH - ACCESSORY INSP.",
        "302 MH Perm Foundation": "301-MH PEM. FOUNDATION",
        "303 MH-Final": "303-MH - FINAL**",
        "400 Underfloor Frame": "400-UNDERFLOOR FRAME",
        "401 Shear Nail-Ext": "401-SHEAR NAIL-EXT",
        "402 Shear Nail-Int": "402-SHEAR NAIL-INT",
        "403 Roof Deck Nail": "406-ROOF DECK NAIL",
        "404 Rough Frame": "404-ROUGH FRAME",
        "405 Ext. Lath/Siding": "405-EXT. LATH/SLIDING",
        "406 Drywall": "406-DRYWALL",
        "407 Firewall": "407-FIREWALL",
        "408 Green/Gray/Purple-BD": "408-GREEN/GRAY/PURPLE-BD",
        "409 Wet Wall": "409-WET WALL",
        "410 Structural Misc/T-Bar": "410-STRUCTURAL MISC/T-BAR",
        "411 Roof/In Progress": "411-ROOF/IN-PROGRESS",
        "412 Window Replacement": "412-WINDOW REPLACEMENT",
        "413 Firewall Penetration": "413-FIREWALL PENETRATION",
        "414 Structural Other": "414-STRUCTURAL. OTHER",
        "501 Conduit/Underground": "501-CONDUIT/UNDERGROUND",
        "502 Service Entrance": "502-SERVICE ENTRANCE",
        "503 Rough Electrical": "503-ROUGH ELECTRICAL",
        "504 Bonding/Grounding": "504-BONDING/GROUNDING",
        "505 Electric Restore Service": "505-ELECTRIC RESTORE SERVICE",
        "507 Electric Meter Release": "507-ELECTRIC METER RELEASE",
        "600 Underfloor Insulation": "600-UNDERFLOOR INSULATION",
        "601 Framing Insulation": "601-FRAMING INSULATION",
        "602 Ceiling Insulation": "602-CEILING INSULATION",
        "700 Ground Plumbing": "700-GROUND PLUMBING",
        "701 Underfloor Plumbing": "701-UNDERFLOOR PLUMBING",
        "702 Rough Plumbing": "702-ROUGH PLUMBING",
        "703 Shower Pan Test": "703-SHOWER PAN TEST",
        "704 Water Service/Piping": "704-WATER SERVICE/PIPING",
        "705 Water Heater": "705-WATER HEATER",
        "706 Gas Pressure Test/Piping": "706-GAS PRESSURE TEST/PIPING",
        "707 Gas Meter Release": "707-GAS METER RELEASE",
        "708 Gas Restore Service": "708-GAS RESTORE SERVICE",
        "801 CMU-Lifts 1,2,3...": "801-CMU - LIFTS 1,2,3...",
        "900 Site Check/Pre-Gunite": "900-SITE CHECK/PRE-GUNITE",
        "901 Bond CVTY/Deck": "901-BOND CVTY/DECK",
        "902 Pool Fence/Door Alarm": "902-POOL FENCE/DOOR ALAR",
        "903 Pool Prefinal": "903-POOL PREFINAL",
        "904 Pool/Spa Final": "904-POOL/SPA FINAL**",
        "925 Furnace Replacement": "925-HVAC FURNACE REPLACEMENT",
        "926 Rough Mechanical": "926-ROUGH MECHANICAL",
        "930 A/C Condenser": "930-A/C CONDENSER",
        "931 Wall Heater": "931-WALL HEATER",
        "932 HVAC Package Unit": "932-T-BAT MECHANICAL",
        "950 Building Final": "950-BUILDING FINAL**",
        "951 Electrical Final": "951-ELECTRICAL FINAL**",
        "952 Plumbing Final": "952-PLUMBING FINAL**",
        "953 Mechanical Final": "953-MECHANICAL FINAL**",
        "954 Grading Final": "954-GRADING FINAL**",
        "955 Demolition Final": "955-DEMOLITION FINAL**",
    }
               
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

                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddInspector_Input"]'))
                        ).click()
                time.sleep(1)
                try:
                        WebDriverWait(driver, '20').until(
                        EC.element_to_be_clickable((By.XPATH, "//li[contains(.,'"+ inspect +"')]"))
                        ).click()
                except:
                        WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddInspector_Input"]'))
                        ).click()
                time.sleep(2)

                defaultDate = setDate[0]
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_ddSetDefault_Input"]'))
                        ).send_keys(defaultDate)

                scheduled = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calScheduledDate$dateInput']"))
                        )
                scheduled.send_keys(Keys.CONTROL + "a")
                scheduled.send_keys(Keys.DELETE)
                scheduled.send_keys(scheduleDate)

                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$ddScheduleTime']"))
                        ).send_keys(scheduleTime)
                
                
                completed = WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$calCompletedDate$dateInput']"))
                        )
                completed.send_keys(completeDate)

                secondTime = driver.find_element(By.XPATH, "//input[@name = 'ctl08$ddCompletedTime']")
                secondTime.send_keys(completeTime)

                res = result[0]
                finalResult= WebDriverWait(driver, '20').until(
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

                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl08_btnSave"]'))
                        ).click()


                driver.switch_to.parent_frame()
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="modalPage"]/div[2]/div/div/table/tbody/tr/td/img[1]'))
                        ).click()
                time.sleep(3)
                WebDriverWait(driver, '20').until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@id='overlay']"))
                        )
                WebDriverWait(driver, '20').until(
                        EC.presence_of_element_located((By.NAME, 'FRMPERMIT'))
                        )
                driver.switch_to.frame("FRMPERMIT")

    print('program finished')


