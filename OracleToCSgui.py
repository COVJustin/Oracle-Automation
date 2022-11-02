import PySimpleGUI as sg
import threading
import OracleToCS
import os
import io
import csv
import zipfile
import pandas as pd

dic = {"": [{"sub": ""}], "SINGLE FAMILY RESIDENTIAL": [{"sub": ""}, {"sub": "ACCESSORY STRUCTURE/SHED"}, {"sub": "ADDITION"}, {"sub": "ALTERATION/REMODEL"}, {"sub": "RE-ROOF"}, {"sub": "UP TO 2 WINDOWS REPLACEMENT"}, {"sub": "3 OR MORE WINDOWS REPLACEMENT"}, {"sub": "SIDING REPLACEMENT"}, {"sub": "KITCHEN REMODEL ONLY"}, {"sub": "BATH REMODEL ONLY"}, {"sub": "CARPORT/GARAGE"}, {"sub": "ADU"}, {"sub": "DECK/PATIO COVER"}, {"sub": "FOUNDATION ONLY"}, {"sub": "INSULATION ONLY"}, {"sub": "RETAINING WALL"}, {"sub": "POOL/SPA"}, {"sub": "FIRE DAMAGE REPAIR"}, {"sub": "CHANGE OF OCCUPANCY"}, {"sub": "NEW DWELLING"}, {"sub": "MASTER PLAN MODEL RESIDENCE"}, {"sub": "STOP WORK"}], "MULTI FAMILY RESIDENTIAL": [{"sub": ""}, {"sub": "ACCESSORY STRUCTURE/SHED"}, {"sub": "ALTERATION/REMODEL"}, {"sub": "SIDING REPLACEMENT"}, {"sub": "UP TO 2 WINDOWS REPLACEMENT"}, {"sub": "3 OR MORE WINDOWS REPLACEMENT"}, {"sub": "RE-ROOF WITH EQUIPMENT"}, {"sub": "RE-ROOF WITH OUT EQUIPMENT"}, {"sub": "NON-STRUCTURAL BATHROOM REMODEL"}, {"sub": "NON-STRUCTURAL KITCHEN REMODEL"}, {"sub": "ADDITION"}, {"sub": "DECK/PATIO COVER"}, {"sub": "CARPORT/GARAGE"}, {"sub": "ADU"}, {"sub": "POOL/SPA"}, {"sub": "RETAINING WALL"}, {"sub": "FOUNDATION ONLY"}, {"sub": "CHANGE OF OCCUPANCY"}, {"sub": "NEW RESIDENTIAL UNIT"}, {"sub": "MASTER PLAN MODEL UNIT"}, {"sub": "NEW BUILDING"}, {"sub": "DEMOLITION - MULTI FAMILY"}, {"sub": "INTERIOR DEMO ONLY"}, {"sub": "INSULATION ONLY"}, {"sub": "FIRE DAMAGE REPAIR"}, {"sub": "STOP WORK"}], "BUILDING COMMERCIAL": [{"sub": ""}, {"sub": "TENANT IMPROVEMENT"}, {"sub": "COMMERCIAL TENANT IMPROVEMENT - NO OCC CHANGE"}, {"sub": "MIXED USE T.I."}, {"sub": "INTERIOR DEMO ONLY"}, {"sub": "ALTERATION/REMODEL"}, {"sub": "RE-ROOF WITH OUT EQUIPMENT"}, {"sub": "RE-ROOF WITH EQUIPMENT"}, {"sub": "ADDITION"}, {"sub": "ADDRESS CHG/CRTN"}, {"sub": "ACCESSORY STRUCTURE/SHED/STORAGE"}, {"sub": "FOUNDATION ONLY"}, {"sub": "PARKING STRUCTURE/GARAGE"}, {"sub": "POOL/SPA"}, {"sub": "RETAINING WALL"}, {"sub": "SIGN"}, {"sub": "MONUMENT SIGN"}, {"sub": "CELL-TOWER/CO-LOCATION/EQUIPMENT"}, {"sub": "TEMPORARY"}, {"sub": "STATUE/ART STRUCTURE"}, {"sub": "NEW MIXED USE"}, {"sub": "NEW BUILDING"}, {"sub": "FIRE DAMAGE REPAIR"}, {"sub": "CHANGE OF OCCUPANCY"}, {"sub": "STOP WORK"}], "ELECTRICAL RESIDENTIAL": [{"sub": ""}, {"sub": "GENERATOR"}, {"sub": "RECONNECT"}, {"sub": "TEMP POWER POLE"}, {"sub": "ALTERATION/REWIRE"}, {"sub": "EVR CHARGER"}, {"sub": "BACKUP BATTERY"}, {"sub": "UP TO 324A"}, {"sub": "325A TO 1000A"}, {"sub": "1000A + PANEL"}], "ELECTRICAL COMMERCIAL": [{"sub": ""}, {"sub": "GENERATOR"}, {"sub": "TRANSFORMER"}, {"sub": "ALTERATION/REWIRE"}, {"sub": "BACKUP BATTERY"}, {"sub": "EVR CHARGER"}, {"sub": "RECONNECT"}, {"sub": "UP TO 324A"}, {"sub": "325A TO 1000A"}, {"sub": "1000A + PANEL"}, {"sub": "TEMPORARY POLE OVER 324A"}, {"sub": "TEMPORARY POLE UP TO 324A"}], "MECHANICAL RESIDENTIAL": [{"sub": ""}, {"sub": "AC CONDENSER ONLY"}, {"sub": "DUCT REPLACEMENT"}, {"sub": "FURNACE ONLY"}, {"sub": "HVAC"}, {"sub": "WALL HEATER REPLACEMENT"}, {"sub": "GAS INSERTS"}, {"sub": "FURNACE AND/OR AC ONLY"}], "MECHANICAL COMMERCIAL": [{"sub": ""}, {"sub": "EQUIPMENT"}, {"sub": "FURNACE"}, {"sub": "HVAC"}, {"sub": "KITCHEN HOOD"}, {"sub": "RADIANT HEATER"}], "PLUMBING RESIDENTIAL": [{"sub": ""}, {"sub": "GAS LINE REPLACEMENT"}, {"sub": "GAS METER"}, {"sub": "PLUMBING FIXTURES"}, {"sub": "SUMP PUMP"}, {"sub": "TANKLESS WATER HEATER"}, {"sub": "WATER HEATER"}, {"sub": "WATER LINE REPLACEMENT"}, {"sub": "NEW GASLINE"}, {"sub": "NEW WATERLINE"}, {"sub": "CLEANOUT"}, {"sub": "SOLAR THERMAL"}, {"sub": "DWV"}, {"sub": "NEW SEWER LINE"}], "PLUMBING COMMERCIAL": [{"sub": ""}, {"sub": "BOILER"}, {"sub": "BUILDING SEWER REPLACEMENT"}, {"sub": "GAS LINE REPLACEMENT"}, {"sub": "GAS METER RECONNECT"}, {"sub": "INTERCEPTOR"}, {"sub": "PLUMBING FIXTURES"}, {"sub": "SUMP PUMP"}, {"sub": "TANKLESS WATER HEATER"}, {"sub": "WATER HEATER REPLACEMENT"}, {"sub": "WATER LINE REPLACEMENT"}, {"sub": "NEW SEWER LINE"}], "RESIDENTIAL SOLAR": [{"sub": ""}, {"sub": "RESIDENTIAL PV 15KW OR LESS"}, {"sub": "RESIDENTIAL PV ABOVE 15KW"}], "COMMERCIAL SOLAR": [{"sub": ""}, {"sub": "COMMERCIAL PV 50KW OR LESS"}, {"sub": "COMMERCIAL SOLAR 51KW TO 250KW"}, {"sub": "COMMERCIAL SOLAR ABOVE 250KW"}]}

def long_operation_thread(p, pf, cu, cp, t, st, d, f, i, pr, a, window):
    OracleToCS.transfer('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', OracleToCS.driver_setup(), p.upper(), pf, cu, cp, t, st, d, f, i, pr, a)
    if f == True:
        window["Status"].update(p + " Has Finished Transferring ! DON'T FORGET TO PAY OUT FEES !")
    window["Status"].update(p + " Has Finished Transferring !")
    window.refresh()

sg.theme("DarkGray2")
inputlayout = [[sg.Text("Select Permit Folder: ", size=(15, 1)), sg.Input(key="PermitFolder"), sg.FolderBrowse(key="PermitFolder")],
         [sg.Text('CS Username: ', size=(15, 1)), sg.InputText(key='CentralUser')],
         [sg.Text('CS Password: ', size=(15, 1)), sg.InputText('', key='CentralPassword', password_char='*')],
         [sg.Text('Permit Number: ', size=(15, 1)), sg.InputText(key='Permit', change_submits=True)],
         [sg.StatusBar("", size=(58, 10), key='Description')]
        ]
selectlayout = [
         [sg.Text('Type: ', size=(7, 1)), sg.Combo(list(dic.keys()),enable_events=True, default_value='',key='Type', size=(24, 1), readonly=True)],
         [sg.Text('Subtype: ', size=(7, 1)), sg.Combo([],default_value='',key='SubType', size=(24, 1), readonly=True)],
         [sg.Text('', size=(19, 2))],
         [sg.Text('Sections To Be Changed:', size=(19, 1))],
         [sg.Checkbox('Description', key='Desc',default=True)],
         [sg.Checkbox('Fees and Payments', key='Fees',default=True)],
         [sg.Checkbox('Inspections', key='Ins',default=True)],
         [sg.Checkbox('Plan Reviews', key='PR',default=True)],
         [sg.Checkbox('Attachments', key='Attach',default=True)]
        ]
startlayout = [[sg.Push(), sg.Button("Transfer", size=(8, 2)), sg.Push()],
         [sg.StatusBar("", size=(20, 1), key='Status')]
         ]
toplayout = [sg.Column(inputlayout), sg.Column(selectlayout)]
layout = [toplayout, startlayout]

window = sg.Window('OracleToCS', layout, size=(850,375), finalize=True)
descup = window['Description'].update
cache = open("cache.txt", "r")
cachelogin = cache.readline()
cachearray = cachelogin.split("#")
if len(cachearray) == 3:
    window["PermitFolder"].update(cachearray[0])
    window["CentralUser"].update(cachearray[1])
    window["CentralPassword"].update(cachearray[2])
input_key_list = [key for key, value in window.key_dict.items()
    if isinstance(value, sg.Input)]
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    else:
        if event == "Transfer":
            if all(map(str.strip, [values[key] for key in input_key_list])):
                window['Status'].update("Running Transfer...")
                if (values["PermitFolder"] + "#" + values["CentralUser"] + "#" + values["CentralPassword"]) != cachelogin:
                    with open('cache.txt', 'w') as newcache:
                        newcache.write(values["PermitFolder"] + "#" + values["CentralUser"] + "#" + values["CentralPassword"])
                if os.path.exists(values["PermitFolder"] + "/" + values["Permit"].upper() + ".zip"):
                    threading.Thread(target=long_operation_thread, args=(values["Permit"].upper(), values["PermitFolder"], values["CentralUser"], values["CentralPassword"], values["Type"], values["SubType"], values["Desc"], values["Fees"], values["Ins"], values["PR"], values["Attach"], window), daemon=True).start()
                    z = zipfile.ZipFile(values["PermitFolder"] + "/" + values["Permit"].upper() + ".zip")
                    if (values["Permit"].upper() + " Fees.csv") in z.namelist() and values["Fees"] == True:
                        outputstr = "REMEMBER TO PAY OUT FEES !!"
                        with zipfile.ZipFile(values["PermitFolder"] + "/" + values["Permit"].upper() + ".zip", 'r') as zin:
                            feedata = io.StringIO(zin.read(values["Permit"].upper() + " Fees.csv").decode('utf-8'))
                            reader = csv.reader(feedata)
                            fd = list(reader)
                        fd.pop(0)
                        lastdate = ""
                        for row in fd:
                            if row[3] == "DUE":
                                outputstr += "\nDUE: " + row[0].partition(" = ")[0] + " = " + str(row[1])
                            if row[6] != "":
                                lastdate = row[6]
                        outputstr += "\nLAST PAYMENT DATE: " + lastdate
                        sg.Popup(outputstr, no_titlebar = True, grab_anywhere = True, keep_on_top = True, modal = True)
                else:
                    window['Status'].update("Invalid Permit")
            else:
                window['Status'].update("Please Complete All Fields")
        elif event == "Type":
            item = values[event]
            title_list = [i["sub"] for i in dic[item]]
            window['SubType'].update(value=title_list[0], values=title_list)
        elif os.path.exists(values["PermitFolder"] + "/" + values["Permit"].upper() + ".zip"):
            with zipfile.ZipFile(values["PermitFolder"] + "/" + values["Permit"].upper() + ".zip", 'r') as zin:
                with zin.open(values["Permit"].upper() + " Information.csv") as infofile:
                    inforeader = pd.read_csv(infofile)
                    infoData = pd.DataFrame(inforeader)
                descup("RESVCOM: " + infoData.at[0, 'Residential/Commercial'] + "\n\nDESCRIPTION:\n" + infoData.at[0, 'Oracle Description'])