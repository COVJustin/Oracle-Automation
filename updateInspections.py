import csv
import os
import io
import zipfile
import tempfile
import pandas as pd
import re
from datetime import datetime

def updateZip(zipname, infofile):
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)           
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                if item.filename != infofile:
                    zout.writestr(item, zin.read(item.filename))
                else:
                    with zin.open(infofile) as inf:
                        inforeader = pd.read_csv(inf)
                        infoData = pd.DataFrame(inforeader)
                    for i in range(len(infoData)):
                        if infoData.at[i, "Inspection Type"] == "901-BOND CVTY/DECK":
                            infoData.at[i, "Inspection Type"] = "901-BOND. CVTY/DECK"
                            print(infofile)
                    infoData.to_csv(item.filename, index=False, header=True)
                    zout.write(item.filename)
                    os.remove(item.filename)
    os.remove(zipname)
    os.rename(tmpname, zipname)


def update():
    with open("C:/Users/amadeo.rosario/Documents/Original Mass File.csv", "r", newline='', encoding='utf8') as extractedPermits:
        csvreader = csv.reader(extractedPermits)
        permitList = list(csvreader)
    permitList.pop(0)
    for z in range(len(permitList)):
        permit = permitList[z][0]
        if os.path.exists("C:/Users/amadeo.rosario/Documents/All Permit Extracts/" + permit + ".zip"):
            z = zipfile.ZipFile("C:/Users/amadeo.rosario/Documents/All Permit Extracts/" + permit + ".zip")
            if (permit + " Inspection.csv") in z.namelist():
                z.close()
                remake = False
                with zipfile.ZipFile("C:/Users/amadeo.rosario/Documents/All Permit Extracts/" + permit + ".zip", 'r') as zin:
                    with zin.open(permit + " Inspection.csv") as inf:
                        inforeader = pd.read_csv(inf)
                        infoData = pd.DataFrame(inforeader)
                    for i in range(len(infoData)):
                        if infoData.at[i, "Inspection Type"] == "901-BOND CVTY/DECK":
                            remake = True
                if remake:
                    updateZip("C:/Users/amadeo.rosario/Documents/All Permit Extracts/" + permit + ".zip", permit + " Inspection.csv")

update()