import csv
import os
import zipfile
import tempfile
import pandas as pd
import re
from datetime import datetime

def updateZip(zipname, filename, data, data2):
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)           
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))
                else:
                    with zin.open(filename) as infofile:
                        inforeader = pd.read_csv(infofile)
                        infoData = pd.DataFrame(inforeader)
                    try:
                        d1 = datetime.strptime(infoData.at[0, 'Applied'], "%m/%d/%y")
                        exp = re.findall('\d{1,2}[/]\d{1,2}[/]\d{1,2}', infoData.at[0, 'Expired'])
                        if len(exp) > 0:
                            infoData.at[0, 'Expired'] = exp[0]
                        d2 = datetime.strptime(infoData.at[0, 'Expired'], "%m/%d/%y")
                        if (d2-d1).days <= 1:
                            infoData.at[0, 'Issued'] = infoData.at[0, 'Expired']
                            infoData.at[0, 'Expired'] = ""
                    except TypeError:
                        print("Cannot compare dates")
                    infoData.insert(0, "Parcel ID", [data], True)
                    infoData.insert(1, "Parcel Address", [data2], True)
                    print(infoData)
                    infoData.to_csv(item.filename, index=False, header=True)
                    zout.write(item.filename)
                    os.remove(item.filename)

    # replace with the temp archive
    os.remove(zipname)
    os.rename(tmpname, zipname)

def update():
    with open("C:/Users/amadeo.rosario/Documents/Original Mass File.csv", "r", newline='', encoding='utf8') as extractedPermits:
        csvreader = csv.reader(extractedPermits)
        permitList = list(csvreader)
    permitList.pop(0)
    for z in range(len(permitList)):
        permit = permitList[z][0]
        if os.path.exists("C:/Users/amadeo.rosario/Documents/All Permit Extracts (TEST)" + "/" + permit + ".zip"):
            updateZip("C:/Users/amadeo.rosario/Documents/All Permit Extracts (TEST)" + "/" + permit + ".zip", permit + " Information.csv", permitList[z][66], permitList[z][110])

update()
