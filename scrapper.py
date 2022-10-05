from gettext import find
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
from datetime import datetime as dt
import zipfile
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
def login(url, driver, permitFile, downloadFileLocation, permitFileLocation, oracle_user, oracle_pass):
    with open(permitFile, "r", newline='', encoding='utf8') as extractedPermits:
        csvreader = csv.reader(extractedPermits)
        permitList = list(csvreader)
    permitList.pop(0)
    print("logging in to Oracle....")
    driver.get(url)
    driver.maximize_window()
    
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//oj-menu-button[@id='switchProfileMenu']/button/div"))
            )
    time.sleep(5)
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//oj-menu-button[@id='switchProfileMenu']/button/div"))
            ).click()
    time.sleep(1)
    WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Sign In')]"))
            ).click()

    oracleLogin = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='idcs-signin-basic-signin-form-username']"))
            )
    
    oraclePassword = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='idcs-signin-basic-signin-form-password|input']"))
            )

    oracleButton = WebDriverWait(driver, '45').until(
            EC.presence_of_element_located((By.XPATH, "//oj-button[@id='idcs-signin-basic-signin-form-submit']/button/div"))
            )
    oracleLogin.send_keys(oracle_user)
    oraclePassword.send_keys(oracle_pass)
    oracleButton.click()
    print("successfully logged in")
    for z in range(len(permitList)):
        permit = permitList[z][0]
        error = open(permitFileLocation + "/Error Catcher.txt", "a")
        try:
            oracle_search = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='srchListC_input|input']"))
                    )
            oracle_search.send_keys(Keys.CONTROL + "a")
            oracle_search.send_keys(Keys.DELETE)
            oracle_search.send_keys(permit)
            oracle_search.send_keys(Keys.ENTER)

            try:
                time.sleep(1)
                driver.find_element(By.XPATH, "//button[@id='ojMessageDialogOKBtn']/div/span").click()
            except (ElementNotInteractableException, NoSuchElementException):
                print("proceed with no pop up")
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '" + permit + "')]"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(.,'Print Permit')]"))
                    )

            # Get Basic Permit Info
            time.sleep(1)
            oracleStatus = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicationInformation']/div/div/div/div[2]/span"))
                    ).text
            oracleDesc = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewDescription']/div/div/div/div[2]/span"))
                    ).text
            if len(oracleDesc) > 46:
                oracleDesc = oracleDesc[:46]
            oracleApplyDate = WebDriverWait(driver, '45').until(
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
            applicant = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicant']/div[2]/div/div/div[2]"))
                    ).text
            primCon = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicant']/div/div/div/div[2]"))
                    ).text
            phone = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicant']/div/div/div[3]/div[2]"))
                    ).text
            email = WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='overviewApplicant']/div/div/div[4]/div[2]"))
                    ).text
            time.sleep(1)
            statusDic = {
                "Approved": "APPROVED",
                "Expired": "EXPIRED",
                "Permit issued": "ISSUED",
                "Inspection": "ISSUED",
                "Plan review": "PLAN CHECK",
                "Submitted": "APPLIED",
                "Void": "VOID",
                "Denied": "DENIED",
                "Withdrawn": "WITHDRAWN",
            }

            status = statusDic[oracleStatus]
            desc = oracleDesc + " " + permit
            applyDate = oracleApplyDate
            expDate = oracleExpDate
            issueDate = oracleIssDate
            valuation = ""

            # Get Valuation & Type (Not sure how to tackle ATM)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@id='permitDetails']/a/span"))
                    ).click()
            #oracleVal = WebDriverWait(driver, '45').until(
            #        EC.presence_of_element_located((By.XPATH, "//input[@id='ccas20_genJobCost']"))
            #        ).text
            #print(oracleVal)
            resvcom = WebDriverWait(driver, '30').until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#cf-fields111 .oj-switch-track, #cf-fields268 .oj-switch-track, #cf-fields237 .oj-switch-track"))
                    ).get_attribute('checked')
            oracleType = "RESIDENTIAL"
            if resvcom:
                oracleType = "COMMERCIAL"
            
            infodf = pd.DataFrame([[status, applicant, desc, oracleType, applyDate, expDate, issueDate, primCon, phone, email]],columns=["Status", "Applicant", "Description", "Residential/Commercial", "Applied", "Expired", "Issued", "Primary Contact", "Primary Contact Phone", "Primary Contact Email"])  
            infodf.to_csv(permitFileLocation + "/" + permit + " Information.csv", index=False, header=True)

            # Get Fees
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
                    ).click()
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//li[9]/a/span/span"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#PSCLNP_RECORD_DETAIL_of_DEFAULT-feeRecord-feeItem-Download-DownloadButton .psc-sui-icon-placeholder"))
                    ).click()
            time.sleep(5)
            shutil.move(downloadFileLocation + '/Fees and Payments.csv', permitFileLocation + "/" + permit + ' Fees.csv')

            # Get Inspections
            skipInspec = False
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//div/ul/li[7]/a/span/span"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#ice_inspection_list-Download-DownloadButton .psc-sui-icon-placeholder"))
                    ).click()
            time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//button[@id='ojAlertDialogOKBtn-5' or @id='ojAlertDialogOKBtn-2' or @id='ojAlertDialogOKBtn-0']/div/span").click()
                time.sleep(2)
                skipInspec = True
            except (ElementNotInteractableException, NoSuchElementException):
                shutil.move(downloadFileLocation + '/Inspection.csv', permitFileLocation + "/" + permit + ' Inspection.csv')
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
                with open(permitFileLocation + "/" + permit + " Inspection.csv", "r", newline='', encoding='utf8') as inspecfile:
                    inspecreader = csv.reader(inspecfile)
                    inspecData = list(inspecreader)
                inspecData.pop(0)
                for i in inspecData:
                    i.append("")
                for i in range(len(inspecData)):
                    comments = ""
                    if inspecData[i][1] in inspectDict:
                        inspecData[i][1] = inspectDict[inspecData[i][1]]
                        inspecData[i][14] = inspecData[i][14].upper()
                        inspecData[i][17] = inspecData[i][17].upper()
                        if inspecData[i][17] != "APPROVED" and inspecData[i][17] != "":
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#inspectionListRelatedAction" + str(i) + "_menubutton-container .psc-sui-icon-placeholder"))
                                    ).click()
                            WebDriverWait(driver, '45').until(
                                    EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'View Detail')]"))
                                    ).click()
                            try:
                                time.sleep(1)
                                driver.find_element(By.XPATH, "//button[@id='ojMessageDialogOKBtn']/div/span").click()
                            except (ElementNotInteractableException, NoSuchElementException):
                                print("proceed with no pop up")
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, "//span[contains(.,'View Summary Report')]"))
                                    )
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, "//li[2]/a/span/span"))
                                    ).click()
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, "//input[@id='oj-inputsearch-input-simpleSearchInputinspectionDetailCommentComponent-search']"))
                                    )
                            try:
                                time.sleep(2)
                                inspecText = driver.find_element(By.XPATH, "//iframe[contains(@id,'inspectionDetailCommentComponent')]").get_attribute('srcdoc')
                                comments += inspecText.replace("</p>", "\n").replace("<div>", "").replace("</div>", "").replace("<p>", "")
                            except (ElementNotInteractableException, NoSuchElementException):
                                print("no comments")
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.XPATH, "//oj-button[@id='navigationBackButton']/button/div/span"))
                                    ).click()
                            WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#ice_inspection_list-Download-DownloadButton .psc-sui-icon-placeholder"))
                                    )
                            time.sleep(3)
                        inspecData[i][20] = comments
                    else:
                        error.write(permit + " inspection type not found: " + inspecData[i][1] + "\n")
                inspecdf = pd.DataFrame(columns=["Inspection","Inspection Type","Status","Required","Permit","Permit Type","Permit Description","Address","Address Line 2","City","Preferred Date","Preferred Time","Ready By","Preferred Inspector","Inspector","Scheduled","Completed","Result","Reinspected By","Reinspection Of","Comments"])
                for i in range(len(inspecData)):
                    inspecdf2 = pd.DataFrame([inspecData[i]],columns=["Inspection","Inspection Type","Status","Required","Permit","Permit Type","Permit Description","Address","Address Line 2","City","Preferred Date","Preferred Time","Ready By","Preferred Inspector","Inspector","Scheduled","Completed","Result","Reinspected By","Reinspection Of", "Comments"])
                    inspecdf = inspecdf.append(inspecdf2,ignore_index=True)
                inspecdf.to_csv(permitFileLocation + "/" + permit + " Inspection.csv", index=False, header=True)

            # Get Reviews
            reviewDic = {
                "Planning": "PLNG-PROJECT REVIEW",
                "Building": "BLDG-PLAN REVIEW",
                "Water": "PW-WATER",
                "Flood Wastewater": "VSFCD-SEWER",
                "Fire": "VFPD-FIRE PLAN REVIEW",
                "Public Works-Flood Zone": "PW-FLOODPLAIN REVIEW",
                "Public Works-Current Dev": "PW-CURRENT DEVELOPMENT",
                "Public Works-Waste Mgmt": "PW-WASTE MGMT. PLAN",
                "Public Works-Traffic": "PW-TRAFFIC ENGINEER",
                "Public Works": "PW-CURRENT DEVELOPMENT",
                "Solano Co-Environmental Health": "SOLANO CO-ENVIRONMENTAL HEALTH"
            }
            
            reviewStatusDic = {
                "Approved": "APPROVED",
                "Revision Required": "PLAN REVIEW CORRECTIONS",
                "Not Required": "REVIEW NOT REQUIRED",
                "Rejected": "DENIED",
                "Canceled": "WITHDRAWN"
            }
            skipRev = False
            time.sleep(1)
            WebDriverWait(driver, '45').until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='permitinfoLabel']"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//li[6]/ul/li[2]/a/span"))
                    ).click()
            WebDriverWait(driver, '45').until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='addPlanReview']"))
                    )
            time.sleep(5)
            try:
                cycleCount = driver.find_element(By.XPATH, "//label[@id='HeaderPlanReviewCycleHeaderLabel|label']").text
                reviewdf = pd.DataFrame(columns=["Submittal Number", "Date Sent", "Review Type", "Reviewer", "Date Due", "Status", "Date Returned", "Notes"])
                cycleCount = int(cycleCount[-1])
                cycleTracker = cycleCount
                commentDic = {}
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//a[@id='prViewPlanCommentsLinkLeft']/span"))
                        ).click()
                try:
                    time.sleep(5)
                    driver.find_element(By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(1) .oj-flex-item .oj-flex-item:nth-child(1)")
                    commentCount = WebDriverWait(driver, '45').until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "psc-lnp-review-panel"))
                                )
                    for i in range(len(commentCount)):
                        commentCycleNum = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") .oj-flex-item .oj-flex-item:nth-child(1)"))
                                ).text[-1]
                        commentRevAndType = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") .oj-flex-item .oj-flex-item:nth-child(2)"))
                                ).text.split(" | ")
                        if len(commentRevAndType) != 2:
                            print("skip comment")
                        else:
                            commentRev = commentRevAndType[0]
                            commentType = commentRevAndType[1]
                            commentText = ""
                            commentTextList = WebDriverWait(driver, '45').until(
                                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".psc-lnp-review-panel:nth-child(" + str(i + 1) + ") p, .psc-lnp-review-panel:nth-child(" + str(i + 1) + ") li"))
                                    )
                            for x in commentTextList:
                                commentText += x.text + "\n"
                            commentDic[commentCycleNum + commentRev + commentType] = commentText
                except NoSuchElementException:
                    print("no comments")
                WebDriverWait(driver, '45').until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='planReviewViewCommentsModal']/div/button/div"))
                        ).click()
                time.sleep(1)
                if cycleCount != 1:
                    for i in range(cycleCount):
                        WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//a[@id='prChangeCycleLink']/span"))
                                ).click()
                        WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//tr[" + str(cycleTracker) + "]/td[8]/div/td/button/div/span"))
                                ).click()
                        body = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//div[3]/div/oj-table/table/tbody"))
                                )
                        rowCount = WebDriverWait(body, '45').until(
                                EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
                                )
                        header = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//label[@id='HeaderPlanReviewOpenByInfoLff|label']"))
                                ).text
                        date1 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', header)[0]
                        for j in range(len(rowCount)):
                            reviewer = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerNameUserTable" + str(j) + "']"))
                                ).text
                            time.sleep(1)
                            if reviewer == "Solano County Environmental Health":
                                reviewer = "Solano Environmental Health"
                                revtype = "Solano Co-Environmental Health"
                            else:
                                revtype = WebDriverWait(driver, '45').until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#prDepartmentUserTable_" + str(j) +" > span"))
                                    ).text
                            date2 = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerDueDateUserTable_" + str(j) + "']"))
                                ).text
                            result = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionStatusUserTable3_" + str(j) + "']"))
                                ).text
                            date3temp = WebDriverWait(driver, '45').until(
                                EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionDttmUserTable_" + str(j) + "']"))
                                ).text
                            date3 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', date3temp)[0]
                            notes = ""
                            tempCheck = str(i + 1) + reviewer + revtype
                            if tempCheck in commentDic:
                                notes += commentDic[tempCheck]
                            reviewdf2 = pd.DataFrame([[i + 1, date1, reviewDic[revtype], reviewer.upper(), date2, reviewStatusDic[result], date3, notes]],columns=["Submittal Number", "Date Sent", "Review Type", "Reviewer", "Date Due", "Status", "Date Returned", "Notes"])
                            reviewdf = reviewdf.append(reviewdf2,ignore_index=True)
                        cycleTracker -= 1
                else:
                    body = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[3]/div/oj-table/table/tbody"))
                            )
                    rowCount = WebDriverWait(body, '45').until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
                            )
                    header = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//label[@id='HeaderPlanReviewOpenByInfoLff|label']"))
                            ).text
                    date1 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', header)[0]
                    for j in range(len(rowCount)):
                        revtype = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#prDepartmentUserTable_" + str(j) +" > span"))
                            ).text
                        reviewer = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerNameUserTable" + str(j) + "']"))
                            ).text
                        date2 = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//td[@id='prReviewerDueDateUserTable_" + str(j) + "']"))
                            ).text
                        result = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionStatusUserTable3_" + str(j) + "']"))
                            ).text
                        date3temp = WebDriverWait(driver, '45').until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='prDecisionDttmUserTable_" + str(j) + "']"))
                            ).text
                        date3 = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', date3temp)[0]
                        notes = ""
                        tempCheck = str(1) + reviewer + revtype
                        if tempCheck in commentDic:
                            notes += commentDic[tempCheck] + " "
                        reviewdf2 = pd.DataFrame([[1, date1, reviewDic[revtype], reviewer.upper(), date2, reviewStatusDic[result], date3, notes]],columns=["Submittal Number", "Date Sent", "Review Type", "Reviewer", "Date Due", "Status", "Date Returned", "Notes"])
                        reviewdf = reviewdf.append(reviewdf2,ignore_index=True)
                reviewdf.to_csv(permitFileLocation + "/" + permit + " Reviews.csv", index=False, header=True)
            except NoSuchElementException:
                skipRev = True
                print("no reviews")
            
            # Change Fees (Needs Optimization)
            feeDic = {
                "Plan Check Fee": "BLG-PLAN REVIEW FEE = .7*{BLDG}",
                "Building Permit Fee": "BLG-BUILDING PERMIT = [1ABUILDPERM22-23]",
                "Title 24 Fee": "BLG-TITLE 24 ENERGY CONSERVATION REVIEW = .1*{BLDG}",
                "Disable Access Review": "BLG-DISABLE ACCESS REVIEW = .15*{BLDG}",
                "State SMIP Fee": "STATE-SMIP RESIDENTIAL = (MAX((JOBVALUE*.00013), .5))",
                "Mechanical Permit Fee": "BLG-MECHANICAL PERMIT = .25*{BLDG}",
                "Electrical Permit Fee": "BLG-ELECTRICAL PERMIT = .2*{BLDG}",
                "General Plan Update Surcharge": "GENERAL PLAN UPDATE SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.05)",
                "Permit Streamlining Surcharge": "PERMIT STREAMLINING SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.03)",
                "Surcharge - Building Technology Fee": "TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)",
                "Surcharge - Engineering Technology Fee": "TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)",
                "Surcharge - Planning Technology Fee": "TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)",
                "State Building Standards Fee - Admin Surcharge": "STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE = .10*[STBSTDS]",
                "State Building Standards Fee": "STATE-BUILDING STANDARDS FEE = .90*[STBSTDS]",
                "CAL Green Building Standards Review": "BLG-CALGREEN BULDING STANDARDS REVIEW = .1*{BLDG}",
                "Fire Site Plan Review": "SITE PLAN REVIEW = [FIRESITEPLAN2022]",
                "Assistant Civil Engineer Review/Inspection": "ASSISTANT CIVIL ENGINEER = QTY*130",
                "C1 PW Waste Management Plan": "C1 GEN FD WASTE MGMT PLAN-BLG = 453",
                "C1, C2, C3 Permit Coordination Fees": "C1 PERMIT COORDINATION FEE = 14",
                "C3 SW Cost Constr. & Demo Recycling": "C3 SW COST CONSTR & DEMO RECYCLING = 8",
                "C2 SW Fee Constr. & Demo Recycling": "C2 SW FEE CONSTR & DEMO RECYCLING = 94",
                "Plumbing Permit Fee": "BLG-PLUMBING PERMIT = .3*{BLDG}",
                "Associate Civil Engineer Review/Inspection": "ASSOCIATE CIVIL ENGINEER = QTY*147",
                "Planning Over-the-Counter Permit Review Fee": "OVER THE COUNTER PERMIT REVIEW APPLICATION FEE = 56",
                "Plan Re-Issuance Fee": "PLAN RE-ISSUANCE FEE - DOES NOT INCLUDE COPY COST = 89",
                "Consultant Review/Inspection": "CONSULTANT REVIEW AND/OR INSPECTION = QTY *1.2",
                "Senior Engineering Technician Review/Inspection": "SENIOR ENGINEERING TECHNICIAN = QTY*138",
                "Engineering Technician Review/Inspection": "ENGINEERING TECH II = QTY*124",
                "Planning Non-Entitlement Permit Review Fee": "NON-ENTITLEMENT PERMIT REVIEW APPLICATION FEE = 215",
                "Senior Civil Engineer Review/Inspection": "SENIOR CIVIL ENGINEER = QTY*164",
                "Encroachment Working w/o a Permit": "BUILDING PERMIT PENALTY = 2 X ORIG PMT",
                "Excavation Working w/o a Permit": "BUILDING PERMIT PENALTY = 2 X ORIG PMT",
                "County Facilities Impact - Multi-Family Age Restr.": "COUNTY FACILITIES-MULTI-FAMILY AGE RESTRICTED = QTY*3975",
                "County Facilities Impact - Second Unit": "COUNTY FACILITIES-SECOND UNIT = QTY* 4536",
                "School Impact - Residential Additions/ADUs": "SCHOOL FEE-RESIDENTIAL ADDITIONS >500 SF = QTY*2.24",
                "Columbus Parkway Impact Payment": "DEV IMPACT-COLUMBUS PKWY PAYMENT = 15432.81",
                "County Facilities Impact - Health Care Facility": "COUNTY FACILITIES-HEALTH CARE FACILITY = QTY*483/1000",
                "County Facilities Impact - Place of Worship": "COUNTY FACILITIES-PLACE OF WORSHIP = QTY*483/1000",
                "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Excise": "HB. I-80 OVERPASS FUND 211 EXCISE TAX = 4021",
                "Transportation Impact - Commercial": "TRANSPORTATION-COMMERCIAL = 4 * QTY",
                "Northgate District 94-1 Impact - Retail": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT = 3398",
                "County Facilities Impact - Congregate Care Fac.": "COUNTY FACILITIES-CONGREGATE CARE FACILITY = QTY*483/1000",
                "County Facilities Impact - Service Commercial": "COUNTY FACILITIES-SERVICE COMMERCIAL = QTY*2097/1000",
                "County Facilities Impact - Single Family": "COUNTY FACILITIES-SINGLE FAMILY = QTY* 9263",
                "Excise Tax - Commercial and Offices": "EXCISE TAX- COMMERCIAL & OFFICES = QTY*.47",
                "GVRD Park Impact - Single Fam Attached per Unit": "GVRD SINGLE FAMILY ATTACHED/UNIT = QTY*12907",
                "Hiddenbr./I-80 Impact - Gen Fund 001 Excise Tax": "HB. I-80 GENERAL FUND 001 EXCISE TAX = 1000",
                "School Impact - Commercial & Offices New/Addition": "SCHOOL FEE-COMMERCIAL & OFFICES = QTY*.36",
                "Transportation Impact - Motels, Hotels": "TRANSPORTATION-MOTELS/HOTELS = QTY * 4768.23",
                "Northgate District 94-1 Impact - Multi-Family": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT = 3398",
                "County Facilities Impact - Riding Arena": "COUNTY FACILITIES-RIDING ARENA = QTY*174/1000",
                "County Facilities Impact - Assembly Uses": "COUNTY FACILITIES-ASSEMBLY USES = QTY*483/1000",
                "County Facilities Impact - Private School": "COUNTY FACILITIES-PRIVATE SCHOOL = QTY*483/1000",
                "County Facilities Impact - Retail": "COUNTY FACILITIES-RETAIL = QTY* 1024/1000",
                "Excise Tax - Residential": "EXCISE TAX- RESIDENTIAL = (MAX(QTY,1)) * 5613",
                "GVRD Park Impact - Multi-Family per Unit": "GVRD MULTI FAMILY/UNIT = QTY*9808",
                "GVRD Park Impact - Mobile Home per Unit": "GVRD MOBILE HOME/UNIT = QTY*8588",
                "Hiddenbr./I-80 Impact - Ovrpass Fund 211 Surcharge": "HB. I-80 OVERPASS FUND 211 SURCHARGE = 979",
                "Transportation Impact - Multi-Family": "TRANSPORTATION-MULTI-FAMILY = QTY * 4768.23",
                "Improvement Permit Inspection Consultant": "CONSULTANT REVIEW AND/OR INSPECTION = QTY *1.2",
                "County Facilities Impact - Hotel, Motel": "COUNTY FACILITIES-HOTEL/MOTEL = QTY*429/1000",
                "County Facilities Impact - Child Day Care Facility": "COUNTY FACILITIES-CHILD DAY CARE FACILITY = QTY*483/1000",
                "County Facilities Impact - Warehouse": "COUNTY FACILITIES-WAREHOUSE = QTY*210/1000",
                "County Facilities Impact - Barn": "COUNTY FACILITIES-BARN = QTY*174/1000",
                "County Facilities Impact - Multi-Family": "COUNTY FACILITIES-MULTI-FAMILY = QTY * 6662",
                "County Facilities Impact - Industrial": "COUNTY FACILITIES-INDUSTRIAL = QTY * 698/1000",
                "County Facilities Impact - Office": "COUNTY FACILITIES-OFFICE = QTY * 1359/1000",
                "GVRD Park Impact - Duplex per Unit": "GVRD DUPLEX/UNIT = QTY*11686",
                "GVRD Park Impact - Single Fam Detached per Unit": "GVRD SINGLE FAMILY DETACHED/UNIT = QTY*14315",
                "Transportation Impact - Industrial": "TRANSPORTATION-INDUSTRIAL = 1.99 * QTY",
                "Sky Valley Improvement District Impact": "DEV IMPACT-SKY VALLEY IMPROVEMENT DIST = 1947",
                "Duplicate Permit Card Fee": "BLG-DUPLICATE PERMIT CARD = 20",
                "Building Permit/Plan Check Extension Request": "PLAN CHECK EXTENSION REQUEST REVIEW FEE = 89",
                "Administrative Citation 1": "BLG-ADMINISTRATIVE CITATION-1 = 267",
                "Northgate District 94-1 Impact - Single Family": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT = 3398",
                "Northgate District 94-1 Impact - Business Office": "DEV IMPACT-NORTHGATE IMPROVEMENT DISTRICT = 3398",
                "Penalty Fee for Work Done w/o Permit": "BUILDING PERMIT PENALTY = 2 X ORIG PMT",
                "Permit Application Fee": "APPLICATION PROCESSING FEE = 32"
            }
            if oracleType == "COMMERCIAL":
                feeDic["State SMIP Fee"] = "STATE-SMIP COMMERCIAL = (MAX((JOBVALUE*.00028), .5))"
            with open(permitFileLocation + "/" + permit + " Fees.csv", "r", newline='') as f:
                reader = csv.reader(f)
                tempData = list(reader)
            tempData.pop(0)
            data = [x for x in tempData if (x[3] == "PAID" or x[3] == "DUE" or x[3] == "REFUND")]

            for i in range(len(data)):
                if data[i][0] in feeDic:
                    if data[i][0] == "C1, C2, C3 Permit Coordination Fees":
                        data[i][1] = float(data[i][1]) - 3.0
                        data.insert(i + 1, ["C2 PERMIT COORDINATION FEE = 2", 2.0, data[i][2], data[i][3], data[i][4], data[i][5], data[i][6]])
                        data.insert(i + 1, ["C3 PERMIT COORDINATION FEE = 1", 1.0, data[i][2], data[i][3], data[i][4], data[i][5], data[i][6]])
                        data[i][0] = feeDic[data[i][0]]
                        i += 2
                    else:
                        data[i][0] = feeDic[data[i][0]]
                else:
                    error.write(permit + " fee not found: " + data[i][0] + "\n")
            feedf = pd.DataFrame(columns=["Fee Description","Amount","Currency","Status","Department","Assessed Date","Payment Date","Invoice"])
            for i in range(len(data)):
                feedf2 = pd.DataFrame([data[i]],columns=["Fee Description","Amount","Currency","Status","Department","Assessed Date","Payment Date","Invoice"])
                feedf = feedf.append(feedf2,ignore_index=True)
            feedf.to_csv(permitFileLocation + "/" + permit + " Fees.csv", index=False, header=True)
            with zipfile.ZipFile(permitFileLocation + "/" + permit + ".zip", 'w') as zipPerm:
                zipPerm.write(permitFileLocation + "/" + permit + " Information.csv", arcname=permit + " Information.csv")
                zipPerm.write(permitFileLocation + "/" + permit + " Fees.csv", arcname=permit + " Fees.csv")
                if skipInspec == False:
                    zipPerm.write(permitFileLocation + "/" + permit + " Inspection.csv", arcname=permit + " Inspection.csv")
                if skipRev == False:
                    zipPerm.write(permitFileLocation + "/" + permit + " Reviews.csv", arcname=permit + " Reviews.csv")
            if os.path.exists(permitFileLocation + "/" + permit + " Information.csv"):
                os.remove(permitFileLocation + "/" + permit + " Information.csv")
            if os.path.exists(permitFileLocation + "/" + permit + " Fees.csv"):
                os.remove(permitFileLocation + "/" + permit + " Fees.csv")
            if os.path.exists(permitFileLocation + "/" + permit + " Inspection.csv"):
                os.remove(permitFileLocation + "/" + permit + " Inspection.csv")
            if os.path.exists(permitFileLocation + "/" + permit + " Reviews.csv"):
                os.remove(permitFileLocation + "/" + permit + " Reviews.csv")
        except (ElementClickInterceptedException, TimeoutException) as errorType:
            error.write(permit + " " + str(errorType) + "\n")
        error.close()
    print('program finished')