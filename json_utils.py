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

if __name__ == '__main__':
    # data_folder = "D://Box Sync/research/paperDrafts/QRank/qrank-sys/rsts/controlled-exps/"
    data_folder = "D://Data/QRank/controlled/server_anomaly/"
    ugly_file_name = "server_anomaly_localization.json"
    pretty_file_name = "server_anomaly_localization_pretty.json"
    data = loadJson(data_folder + ugly_file_name)
    dumpJson(data, data_folder + pretty_file_name)