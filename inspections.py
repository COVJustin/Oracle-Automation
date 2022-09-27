from gettext import find
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime as dt
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
    central_user = "aro"
    central_pass = "Xbox1fanatic!"
    
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
    permType = "RESIDENTIAL"

    status = "ISSUED"
    desc = "675 SQ FT attached aluminum patio cover w/ electrical"
    applyDate = "1/25/21"
    expDate = "3/31/22"
    issueDate = "5/26/21"

    valuation = "20,650.00"

    # Change Reviews
    reviewDic = {
        "Planning": "]/ul/li[12]/div/span[3]",
        "Building": "]/ul/li[3]/div/span[3]",
        "Water": "]/ul/li[22]/div/span[3]",
        "Flood Wastewater": "]/ul/li[30]/div/span[3]",
        "Fire": "]/ul/li[29]/div/span[3]",
        "Public Works-Flood Zone": "]/ul/li[19]/div/span[3]",
        "Public Works-Current Dev": "]/ul/li[16]/div/span[3]",
        "Public Works-Waste Mgmt": "]/ul/li[21]/div/span[3]"
    }
    reviewStatusDic = {
        "Approved": "APPROVED",
        "Revision Required": "PLAN REVIEW CORRECTIONS",
        "Not Required": "REVIEW NOT REQUIRED",
        "Rejected": "DENIED"
    }
    with open("Oracle-Automation/Permits/" + permit + " Reviews.csv", "r", newline='') as file:
        reader2 = csv.reader(file)
        reviewData = list(reader2)
    cycleCounter = 0
    editCounter = 0
    dateTrack = dt.strptime("1/1/01", "%m/%d/%y")
    for i in range(0, len(reviewData)):
        if reviewData[i][1] in reviewDic:
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
            innerframe = WebDriverWait(driver, '20').until(
                    EC.presence_of_element_located((By.NAME, 'rw'))
                    )
            driver.switch_to.frame(innerframe)
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
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnEdit']"))
            ).click()

    # Change Status
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='ctl09_C_ctl00_ddStatus_Input']"))
            ).click()
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

    # Change Valuation
    try:
        time.sleep(5)
        driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnEditAllValuationsBottom']").click()
    except NoSuchElementException:
        WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl11$C$ctl00$btnAddValuation']"))
                ).click()
        driver.switch_to.parent_frame()
        innerframe = WebDriverWait(driver, '20').until(
                EC.presence_of_element_located((By.NAME, 'rw'))
                )
        time.sleep(5)
        driver.switch_to.frame(innerframe)
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
        "Penalty Fee for Work Done w/o Permit": "BUILDING PERMIT PENALTY"
    }

    with open("Oracle-Automation/Permits/" + permit + " Fees.csv", "r", newline='') as f:
        reader = csv.reader(f)
        tempData = list(reader)
    tempData.pop(0)
    data = [x for x in tempData if x[3] != "PEND"]

    transferred = [False] * len(data)
    while False in transferred:
        WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']"))
            ).click()
        driver.switch_to.parent_frame()
        innerframe2 = WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.NAME, 'rw'))
            )
        driver.switch_to.frame(innerframe2)
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
                elif (data[i][0] == "Encroachment Working w/o a Permit" or data[i][0] == "Excavation Working w/o a Permit" or "Penalty Fee for Work Done w/o Permit") and check29 == 0:
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
        WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']"))
            ).click()
        time.sleep(15)
        driver.switch_to.parent_frame()
        WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
        driver.switch_to.frame("FRMPERMIT")

    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnCancelEditAllFeesBottom']"))
            ).click()
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnEditAllFeesBottom']"))
            ).click()
    time.sleep(10)

    # Needs Potential Optimizing
    for i in range(0, len(data)):
        if (data[i][3] == "PAID" or data[i][3] == "DUE"):
            keywrds = [feeDic[item[0]] for item in data]
            if feeDic[data[i][0]] == "STATE-BUILDING STANDARDS FEE" or feeDic[data[i][0]] == "STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE":
                print("skipped")
            if feeDic[data[i][0]] == "C1 PERMIT COORDINATION FEE":
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
    time.sleep(5)
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
            ).click()

    print('program finished')

central_login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', driver_setup(), 'BP-2021-0126')
