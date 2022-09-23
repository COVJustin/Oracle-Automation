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

    print("successfully logged in")

    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.NAME, "FRMPERMIT"))
            )
    driver.switch_to.frame("FRMPERMIT")   

    # Click edit
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl09$C$ctl00$btnEdit']"))
            ).click()

    # Permit Info
    permType = "RESIDENTIAL"

    status = "EXPIRED"
    desc = "675 SQ FT attached aluminum patio cover w/ electrical"
    applyDate = "1/25/21"
    expDate = "3/31/22"
    issueDate = "5/26/21"

    valuation = "20,650.00"

    # Change Status
    firstLetter = status[0]
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@id = 'ctl09_C_ctl00_ddStatus_Input']"))
            ).send_keys(firstLetter)
    
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

    # Change Fees
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
        "Planning Over-the-Counter Permit Review Fee": "OVER THE COUNTER PERMIT REVIEW APPLICATION FEE"
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
    WebDriverWait(driver, '20').until(
            EC.presence_of_element_located((By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnSaveAllFeesBottom']"))
            ).click()

    print('program finished')

central_login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', driver_setup(), 'BP-2021-0126')
