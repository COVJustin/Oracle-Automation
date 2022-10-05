import PySimpleGUI as sg
import threading
import scrapper

def long_operation_thread(p, d, pf, ou, op, window):
    scrapper.login('https://emwp.fa.us2.oraclecloud.com/fscmUI/publicSector.html', scrapper.driver_setup(), p, d, pf, ou, op)
    window.write_event_value('-THREAD-', 'All Permits Have Been Scrapped !')

sg.theme("BlueMono")
layout = [[sg.Text("Select Download Folder: ", size=(19, 1)), sg.Input(key="Download"), sg.FolderBrowse(key="Download")],
         [sg.Text("Select Permit Folder: ", size=(19, 1)), sg.Input(key="PermitFolder"), sg.FolderBrowse(key="PermitFolder")],
         [sg.Text('Oracle Username: ', size=(19, 1)), sg.InputText(key="OracleUser")],
         [sg.Text('Oracle Password: ', size=(19, 1)), sg.InputText('', key='OraclePassword', password_char='*')],
         [sg.Text('Permit File: ', size=(19, 1)), sg.InputText(key='Permit'), sg.FileBrowse(key="PermitFolder")],
         [sg.Button("Scrap")],
         [sg.StatusBar("", size=(20, 1), key='Status')]
         ]

window = sg.Window('OracleScrapper', layout, size=(600,225))
prompt = window['Status'].update
input_key_list = [key for key, value in window.key_dict.items()
    if isinstance(value, sg.Input)]
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Scrap":
        if all(map(str.strip, [values[key] for key in input_key_list])):
            prompt("Running Extract...")
            threading.Thread(target=long_operation_thread, args=(values["Permit"], values["Download"], values["PermitFolder"], values["OracleUser"], values["OraclePassword"], window), daemon=True).start()
        else:
            prompt("Please Complete All Fields")
    elif event == "-THREAD-":
        prompt(values[event])