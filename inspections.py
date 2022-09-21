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

    valuation = "85,766.92"

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

    # Change Valuation
    valuationBtn = driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$btnAddValuation']")
    valuationBtn.click()
    driver.switch_to.parent_frame()
    innerframe = driver.find_element(By.NAME,'rw')
    driver.switch_to.frame(innerframe)
    time.sleep(5)
    driver.find_element(By.XPATH, "//strong[contains(.,'JOB VALUATION = $1.00/EA')]").click()
    driver.find_element(By.XPATH, "//input[@name = 'ctl08$imgBtnAdd']").click()
    time.sleep(5)
    driver.switch_to.parent_frame()
    driver.switch_to.frame("FRMPERMIT")
    valField = driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$rGridValuations$ctl00$ctl04$txtParentQty']")
    valField.send_keys(valuation)
    driver.find_element(By.XPATH, "//input[@name = 'ctl11$C$ctl00$imgBtnSaveAllValuationsTop']").click()
    time.sleep(5)
    
    # Change Fees
    driver.find_element(By.XPATH, "//input[@name = 'ctl12$C$ctl00$imgBtnAddFees']").click()
    time.sleep(5)
    driver.switch_to.parent_frame()
    driver.switch_to.frame(innerframe)

    permitFile = open("Oracle-Automation/Permits/" + permit + ".txt", "r")
    data = permitFile.readlines()

    infolist = []
    for i in data:
        j = i.replace('\t', '').replace('\n', '')
        infolist.append(j)

    print(infolist)
    
    fees = []
    for i in range(0, len(infolist)):
        temp = []
        if infolist[i] == "Plan Check Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "//span[contains(.,'BLG-PLAN REVIEW FEE = .7*{BLDG}')]").click()
        elif infolist[i] == "Building Permit Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-BUILDING PERMIT = [1ABUILDPERM22-23]')]").click()
        elif infolist[i] == "Title 24 Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-TITLE 24 ENERGY CONSERVATION REVIEW = .1*{BLDG}')]").click()
        elif infolist[i] == "Disable Access Review":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-DISABLE ACCESS REVIEW = .15*{BLDG}')]").click()
        # Make if statement later for res v com
        elif infolist[i] == "State SMIP Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'STATE-SMIP RESIDENTIAL = (MAX((JOBVALUE*.00013), .5))')]").click()
        elif infolist[i] == "Mechanical Permit Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-MECHANICAL PERMIT = .25*{BLDG}')]").click()
        elif infolist[i] == "Electrical Permit Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-ELECTRICAL PERMIT = .2*{BLDG}')]").click()
        elif infolist[i] == "General Plan Update Surcharge":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'GENERAL PLAN UPDATE SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.05)')]").click()
        elif infolist[i] == "Permit Streamlining Surcharge":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'PERMIT STREAMLINING SURCHARGE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.03)')]").click()
        elif infolist[i] == "Surcharge - Building Technology Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)')]").click()
        elif infolist[i] == "Surcharge - Engineering Technology Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'TECHNOLOGY SURCHARGE FEE = INT(({BLDG}+{PLUMBLDG}+{ELECBLDG}+{MECHBLDG}+{BLDGFF}+{BLDGFF06}+{BLDG_EFF07}+{RESOL}+{RESOL1}+{BLDG_EFF02}+{MISCELEC2}+{MISCELEC6}+{MISCELEC3}+{MISCELEC1}+{MISCELEC1}+{MISCELEC7}+{MISCELEC}+{MISCELEC4}+{MISCELEC5}+{BLDGFF05}+{BLDG_EFF01}+{MECH}+{PLUMBFF}+{SIGN1}+{SIGN2}+{CELL1}+{CELL}+{DEMO}+{ELECT}+{MECHANICAL}+{PLUMB})*.04)')]").click()
        elif infolist[i] == "State Building Standards Fee - Admin Surcharge":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'STATE-BUILDING STANDARDS FEE-ADMIN SURCHARGE = .10*[STBSTDS]')]").click()
        elif infolist[i] == "State Building Standards Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'STATE-BUILDING STANDARDS FEE = .90*[STBSTDS]')]").click()
        elif infolist[i] == "CAL Green Building Standards Review":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-CALGREEN BULDING STANDARDS REVIEW = .1*{BLDG}')]").click()
        elif infolist[i] == "Fire Site Plan Review":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'SITE PLAN REVIEW = [FIRESITEPLAN2022]')]").click()
        elif infolist[i] == "Assistant Civil Engineer Review/Inspection":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            print(infolist[i])
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'ASSISTANT CIVIL ENGINEER = QTY*130')]").click()
        elif infolist[i] == "C1 PW Waste Management Plan":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C1 GEN FD WASTE MGMT PLAN-BLG = 453')]").click()
        elif infolist[i] == "C1, C2, C3 Permit Coordination Fees":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C1 PERMIT COORDINATION FEE = 14')]").click()
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C2 PERMIT COORDINATION FEE = 2')]").click()
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C3 PERMIT COORDINATION FEE = 1')]").click()
        elif infolist[i] == "C3 SW Cost Constr. & Demo Recycling":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C3 SW COST CONSTR & DEMO RECYCLING = 8')]").click()
        elif infolist[i] == "C2 SW Fee Constr. & Demo Recycling":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'C2 SW FEE CONSTR & DEMO RECYCLING = 94')]").click()
        elif infolist[i] == "Plumbing Permit Fee":
            temp.append(infolist[i])
            num = infolist[i+1]
            num.replace(',','')
            float(num)
            temp.append(num)
            fees.append(temp)
            driver.find_element(By.XPATH, "xpath=//span[contains(.,'BLG-PLUMBING PERMIT = .3*{BLDG}')]").click()
    print('program finished')

central_login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', driver_setup(), 'BP-2022-0788')
