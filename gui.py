import PySimpleGUI as sg
import threading
import inspections

def long_operation_thread(p, d, pf, ou, op, cu, cp, window):
    inspections.login('https://vall-trk.aspgov.com/CommunityDevelopment/default.aspx', 'https://emwp.fa.us2.oraclecloud.com/fscmUI/publicSector.html', inspections.driver_setup(), p, d, pf, ou, op, cu, cp)
    window.write_event_value('-THREAD-', p + ' Has Finished Transferring !')

sg.theme("BlueMono")
layout = [[sg.Text("Select Download Folder: ", size=(19, 1)), sg.Input(key="Download"), sg.FolderBrowse(key="Download")],
         [sg.Text("Select Permit Folder: ", size=(19, 1)), sg.Input(key="PermitFolder"), sg.FolderBrowse(key="PermitFolder")],
         [sg.Text('Oracle Username: ', size=(19, 1)), sg.InputText(key="OracleUser")],
         [sg.Text('Oracle Password: ', size=(19, 1)), sg.InputText('', key='OraclePassword', password_char='*')],
         [sg.Text('Central Square Username: ', size=(19, 1)), sg.InputText(key='CentralUser')],
         [sg.Text('Central Square Password: ', size=(19, 1)), sg.InputText('', key='CentralPassword', password_char='*')],
         [sg.Text('Permit Number: ', size=(19, 1)), sg.InputText(key='Permit', change_submits=True)],
         [sg.Button("Transfer")],
         [sg.StatusBar("", size=(20, 1), key='Status')]
         ]

window = sg.Window('OracleToTrakit', layout, size=(600,275))
prompt = window['Status'].update
input_key_list = [key for key, value in window.key_dict.items()
    if isinstance(value, sg.Input)]
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Transfer":
        if all(map(str.strip, [values[key] for key in input_key_list])):
            prompt("Running Transfer...")
            threading.Thread(target=long_operation_thread, args=(values["Permit"], values["Download"], values["PermitFolder"], values["OracleUser"], values["OraclePassword"], values["CentralUser"], values["CentralPassword"], window), daemon=True).start()
        else:
            prompt("Please Complete All Fields")
    elif event == "-THREAD-":
        prompt(values[event])