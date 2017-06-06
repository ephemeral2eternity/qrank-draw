import json
import pandas as pd

#####################################################################################
## @descr: save a json object to json file
## @params: jsonData ---- the json object of the data
##          fileFullName ---- the file name to save including the full path.
#####################################################################################
def dumpJson(jsonData, fileFullName):
    with open(fileFullName, 'w') as f:
        json.dump(jsonData, f, sort_keys=True, indent=4)

#####################################################################################
## @descr: load json object from json file
## @params: fileFullName ---- the file name to save including the full path.
## @return: data
#####################################################################################
def loadJson(fileFullName):
    json_data = open(fileFullName).read()
    data = json.loads(json_data)
    return data

#####################################################################################
## @descr: dump a list of json objects to a csv file
## @params: data  ---- list of json objects with the same keys
#           fileFullName ---- the file name to save including the full path.
#####################################################################################
def json2csv(data, fileFullName):
    df = pd.DataFrame(data)
    df.to_csv(fileFullName)