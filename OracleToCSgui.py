import PySimpleGUI as sg
import threading
import OracleToCS
import os
import zipfile
import pandas as pd

dic = {"SINGLE FAMILY RESIDENTIAL": [{"sub": "ACCESSORY STRUCTURE/SHED"}, {"sub": "ADDITION"}, {"sub": "ALTERATION/REMODEL"}, {"sub": "RE-ROOF"}, {"sub": "UP TO 2 WINDOWS REPLACEMENT"}, {"sub": "3 OR MORE WINDOWS REPLACEMENT"}, {"sub": "SIDING REPLACEMENT"}, {"sub": "KITCHEN REMODEL ONLY"}, {"sub": "BATH REMODEL ONLY"}, {"sub": "CARPORT/GARAGE"}, {"sub": "ADU"}, {"sub": "DECK/PATIO COVER"}, {"sub": "FOUNDATION ONLY"}, {"sub": "INSULATION ONLY"}, {"sub": "RETAINING WALL"}, {"sub": "POOL/SPA"}, {"sub": "FIRE DAMAGE REPAIR"}, {"sub": "CHANGE OF OCCUPANCY"}, {"sub": "NEW DWELLING"}, {"sub": "MASTER PLAN MODEL RESIDENCE"}, {"sub": "STOP WORK"}], "BUILDING COMMERCIAL": [{"sub": "TENANT IMPROVEMENT"}, {"sub": "COMMERCIAL TENANT IMPROVEMENT - NO OCC CHANGE"}, {"sub": "MIXED USE T.I."}, {"sub": "INTERIOR DEMO ONLY"}, {"sub": "ALTERATION/REMODEL"}, {"sub": "RE-ROOF WITH OUT EQUIPMENT"}, {"sub": "RE-ROOF WITH EQUIPMENT"}, {"sub": "ADDITION"}, {"sub": "ADDRESS CHG/CRTN"}, {"sub": "ACCESSORY STRUCTURE/SHED/STORAGE"}, {"sub": "FOUNDATION ONLY"}, {"sub": "PARKING STRUCTURE/GARAGE"}, {"sub": "POOL/SPA"}, {"sub": "RETAINING WALL"}, {"sub": "SIGN"}, {"sub": "MONUMENT SIGN"}, {"sub": "CELL-TOWER/CO-LOCATION/EQUIPMENT"}, {"sub": "TEMPORARY"}, {"sub": "STATUE/ART STRUCTURE"}, {"sub": "NEW MIXED USE"}, {"sub": "NEW BUILDING"}, {"sub": "FIRE DAMAGE REPAIR"}, {"sub": "CHANGE OF OCCUPANCY"}, {"sub": "STOP WORK"}]}

def long_operation_thread(p, pf, cu, cp, t, st, d, f, i, pr, window):
    OracleToCS.transfer('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', OracleToCS.driver_setup(), p.upper(), pf, cu, cp, t, st, d, f, i, pr)
    if f == True:
        window.write_event_value("-THREAD-", p + " Has Finished Transferring ! DON'T FORGET TO PAY OUT FEES !")
    else:
        window.write_event_value("-THREAD-", p + " Has Finished Transferring !")

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
         [sg.Checkbox('Plan Reviews', key='PR',default=True)]
        ]
startlayout = [[sg.Push(), sg.Button("Transfer", size=(8, 2)), sg.Push()],
         [sg.StatusBar("", size=(20, 1), key='Status')]
         ]
toplayout = [sg.Column(inputlayout), sg.Column(selectlayout)]
layout = [toplayout, startlayout]

window = sg.Window('OracleToCS', layout, size=(850,375))
prompt = window['Status'].update
descup = window['Description'].update
input_key_list = [key for key, value in window.key_dict.items()
    if isinstance(value, sg.Input)]
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Transfer":
        if all(map(str.strip, [values[key] for key in input_key_list])):
            prompt("Running Transfer...")
            threading.Thread(target=long_operation_thread, args=(values["Permit"].upper(), values["PermitFolder"], values["CentralUser"], values["CentralPassword"], values["Type"], values["SubType"], values["Desc"], values["Fees"], values["Ins"], values["PR"], window), daemon=True).start()
        else:
            prompt("Please Complete All Fields")
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
    elif event == "-THREAD-":
        prompt(values[event])