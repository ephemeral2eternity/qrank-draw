from json_utils import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from fig_utils import *
from data_folder import *

###########################################################################
## @descr: Merge networks from two json files and remove repeated networks
## @params: fileName1 --- the file name for the first json files storing network list
##          fileName2 --- the file name for the first json files storing network list
## @output: anomalous_networks ---- dump the merged network list to anomalous-networks.json
def merge_anomalous_networks(fileName1, fileName2):
    nets1 = loadJson(rstsfolder + fileName1)
    nets2 = loadJson(rstsfolder + fileName2)

    anomalous_networks_ases = []
    anomalous_networks = []

    for net in nets1:
        if net["as"] not in anomalous_networks_ases:
            anomalous_networks_ases.append(net["as"])
            anomalous_networks.append({"as":net["as"], "name":net["name"], "type":net["type"]})

    for net in nets2:
        if net["as"] not in anomalous_networks_ases:
            anomalous_networks_ases.append(net["as"])
            anomalous_networks.append({"as": net["as"], "name": net["name"], "type": net["type"]})

    return anomalous_networks

###########################################################################
## @descr: Get the abbreviated AS name by AS number
## @params: asNum --- the AS number to get the AS Name
## @return: asName --- the abbreviated AS number for an ISP denoted by AS number
def get_asname(asNum):
    anomalous_nets = loadJson(rstsfolder+"anomalous-networks.json")
    try:
        asname = anomalous_nets[str(asNum)]["asname"]
    except:
        asname = "AS" + str(asNum)
    return asname


if __name__ == '__main__':
    # transit_network_filename = "anomalous-transit-networks.json"
    # access_network_filename = "anomalous-access-networks.json"

    # merged_nets = merge_anomalous_networks(transit_network_filename, access_network_filename)
    # dumpJson(merged_nets, rstsfolder+"anomalous-networks.json")

    ## Change list of anomalous networks to json
    #anomalous_nets = loadJson(rstsfolder+"anomalous-networks-list.json")
    #anomalous_nets_json = {}
    #for net in anomalous_nets:
    #    anomalous_nets_json[net["as"]] = net
    # dumpJson(anomalous_nets_json, rstsfolder+"anomalous-networks.json")

    # asNum = 174
    # print(get_asname(asNum))

    anomalous_nets = loadJson(rstsfolder + "anomalous-networks-list.json")
    df = pd.DataFrame(anomalous_nets)
    df.to_csv(rstsfolder + "anomalous-networks.csv", sep=",", encoding='utf-8')




