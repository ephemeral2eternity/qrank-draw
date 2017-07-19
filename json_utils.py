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


## Replace the name for nodes by given values for drawing purpose
def replace_node_key(data, keyName, keyValuesToReplace):
    for node,ix in zip(data["nodes"], range(len(data["nodes"]))):
        if keyName in node.keys():
            curKeyVal = node[keyName]
            data["nodes"][ix]["org"+keyName] = curKeyVal
            if curKeyVal in keyValuesToReplace.keys():
                data["nodes"][ix][keyName] = keyValuesToReplace[curKeyVal]
            else:
                data["nodes"][ix][keyName] = ""
        else:
            data["nodes"][ix][keyName] = ""

    return data

if __name__ == '__main__':
    # data_folder = "D://Box Sync/research/paperDrafts/QRank/qrank-sys/rsts/controlled-exps/"
    # data_folder = "D://Data/QRank/controlled/"
    # data_folder = "/Users/chenw/Data/QRank/controlled/"
    ugly_file_name = "device_anomaly_raw.json"
    pretty_file_name = "device_anomaly.json"
    data = loadJson(data_folder + ugly_file_name)

    keyValuesToReplace = {
        "planetlab01.cs.washington.edu":"A1",
        "planetlab02.cs.washington.edu":"A2",
        "planetlab03.cs.washington.edu":"A3",
        "planetlab04.cs.washington.edu":"A4",
        "planetlab1.cs.uoregon.edu":"B1",
        "planetlab3.cs.uoregon.edu":"B2",
        "planetlab4.cs.uoregon.edu":"B3",
        "planetlab1.postel.org":"C1",
        "planetlab4.postel.org":"C2",
        "cache-01.cmu-agens.com":"S1",
        "cache-02.cmu-agens.com":"S2",
        "cache-03.cmu-agens.com":"S3"
    }
    keyName = "name"

    revised_data = replace_node_key(data, keyName, keyValuesToReplace)
    dumpJson(revised_data, data_folder + pretty_file_name)