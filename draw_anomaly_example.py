import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from json_utils import *
import pprint
from fig_utils import *
from drawlibs.plot_qoe_curves import *
from drawlibs.draw_for_anomaly import *
import numpy as np

## Configure the data folders
datafolder = "D:/Data/QRank/20170510/"

imgfolder = datafolder + "imgs/"
rstsfolder = datafolder + "rsts/"
qoesfolder = datafolder + "sessions/qoes/"
latsfolder = datafolder + "sessions/lats/"
linksfolder = datafolder + "links/"
networksfolder = datafolder + "networks/"

# datafolder = "D://Data/QRank/20170510/"
anomaly_file = "merged_anomalies.json"
session_file = "sessions.json"
node_file = "nodes.json"
network_file = "networks.json"


## Get multiple objects by a list of ids.
## The objects can be network, link, isp, session, node, etc.
def get_objects(all_object_file, object_ids):
    all_objects = loadJson(all_object_file)
    objects = [all_objects[str(x)] for x in object_ids]
    return objects

## Get anomalies by denoting the anomaly_id and the session_id the
## anomaly is on.
def get_anomaly(session_id, anomaly_id):
    all_session_anomalies = loadJson(datafolder + anomaly_file)
    session_anomalies = all_session_anomalies[str(session_id)]
    for anomaly in session_anomalies:
        if int(anomaly["id"]) == anomaly_id:
            return anomaly
    return None

## Get session QoEs within a time range
def get_session_qoes_in_range(session_id, startTS, endTS):
    session_qoe_file = qoesfolder + "session_" + str(session_id) + "_qoes.json"
    session_qoes = loadJson(session_qoe_file)
    session_qoes_list = session_qoes["qoes"]
    qoes_to_get = []
    for qoe in session_qoes_list:
        if (float(qoe["timestamp"]) >= startTS) and (float(qoe["timestamp"]) < endTS):
            qoes_to_get.append({"timestamp":float(qoe["timestamp"]),"QoE":float(qoe["QoE"])})

    return qoes_to_get

def get_session_lats_in_range(session_id, startTS, endTS):
    session_lats_file = latsfolder + "session_" + str(session_id) + "_lats.json"
    session_lats = loadJson(session_lats_file)
    lats_to_get = []
    for ts in session_lats.keys():
        if (float(ts) >= startTS) and (float(ts) < endTS):
            lats_to_get.append({"timestamp":float(ts),"latency":float(session_lats[ts])})

    return lats_to_get

def get_lats_stat_in_anomaly(lats, anomalyStart, anomalyEnd):
    all_lats = []
    lats_in_anomaly = []

    for lat in lats:
        all_lats.append(lat["latency"])
        if (float(lat["timestamp"]) >= anomalyStart) and (float(lat["timestamp"]) < anomalyEnd):
            lats_in_anomaly.append(float(lat["latency"]))

    if len(all_lats) > 0:
        all_lat_mn = np.mean(all_lats)
        all_lat_std = np.std(all_lats)
    else:
        all_lat_mn = "Null"
        all_lat_std = "Null"

    if len(lats_in_anomaly) > 0:
        anomaly_lat_mn = np.mean(lats_in_anomaly)
        anomaly_lat_std = np.std(lats_in_anomaly)
    else:
        anomaly_lat_mn = "Null"
        anomaly_lat_std = "Null"

    return {"all_lat_mn": all_lat_mn, "all_lat_std": all_lat_std,
            "anomaly_lat_mn":anomaly_lat_mn, "anomaly_lat_std":anomaly_lat_std}

## Get the node info by the node id
def get_node(node_id):
    all_nodes_info = loadJson(datafolder + node_file)
    node = all_nodes_info[str(node_id)]
    return node

## Get network ids for all networks involved in a session
# @params: session --- the session to get networks
def get_networks_by_session(session):
    unique_network_ids = []
    for hopID in session["hops"].keys():
        hop_nodes = session["hops"][hopID]
        for node_id in hop_nodes:
            node = get_node(node_id)
            node_network_id = node["network"]
            if node_network_id not in unique_network_ids:
                unique_network_ids.append(node_network_id)

    return unique_network_ids

## Get the network info json by the network id
def get_network(network_id):
    networks = loadJson(datafolder + network_file)
    network = networks[str(network_id)]
    return network

## Get probed latencies for all networks involved in a given session within a time range
def get_network_lats_in_range(network_id, startTS, endTS, agent="planetlab"):
    network_lats = loadJson(networksfolder + "network_" + str(network_id) + "_lats.json")
    lats_json = network_lats[agent]
    cur_network_lats_in_range = []
    for ts in lats_json.keys():
        if (float(ts) >= startTS) and (float(ts) <= endTS) and (lats_json[ts] > 0):
            cur_network_lats_in_range.append({"timestamp":float(ts), "latency":lats_json[ts]})
    return cur_network_lats_in_range

def plot_qoes_for_anomaly(session_id, anomaly_id):
    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    # pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period
    session_id = anomaly["session_id"]

    session_qoes = get_session_qoes_in_range(session_id, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_qoes"
    draw_qoes_for_anomaly(session_qoes, draw_start, draw_end, anomaly_start, anomaly_end, img_name, num_intvs=5)


def plot_network_lats_for_anomaly(session_id, anomaly_id, agent="planetlab"):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    network_ids = get_networks_by_session(session)
    networks_details = {}
    for network_id in network_ids:
        networks_details[network_id] = get_network(network_id)

    networks_lats = {}
    networks_lats_stats = []
    for network_id in network_ids:
        networks_lats[network_id] = get_network_lats_in_range(network_id, draw_start, draw_end, agent)
        cur_network_lats_stats = get_lats_stat_in_anomaly(networks_lats[network_id], anomaly_start, anomaly_end)
        cur_network_lats_stats["network"] = networks_details[network_id]["name"] \
                                            + "(AS " + str(networks_details[network_id]["as"]) + ")" \
                                            + "@(" + str(networks_details[network_id]["latitude"]) + "," \
                                            + str(networks_details[network_id]["longitude"]) + ")"
        networks_lats_stats.append(cur_network_lats_stats)

    json2csv(networks_lats_stats, rstsfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_nets_lats_" + agent + ".csv")

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_nets_lats_" + agent
    draw_networks_lats_for_anomaly(networks_lats, networks_details, draw_start, draw_end, anomaly_start, anomaly_end, img_name)

def plot_session_lat_for_anomaly(session_id, anomaly_id):
    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    # pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period
    session_id = anomaly["session_id"]
    session = get_objects(datafolder + session_file, [session_id])[0]

    session_lats = get_session_lats_in_range(session_id, draw_start, draw_end)
    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_lats"
    draw_session_lats_for_anomaly(session_lats, draw_start, draw_end, anomaly_start, anomaly_end, img_name)
    session_lats_stats = get_lats_stat_in_anomaly(session_lats, anomaly_start, anomaly_end)
    session_lats_stats["session_id"] = session_id

    json2csv([session_lats_stats], rstsfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_session_lats.csv")

if __name__ == '__main__':
    # datafolder = "/Users/chenw/Data/QRank/20170510/"

    session_id = 2
    anomaly_id = 36

    ## Ploting params
    pp = pprint.PrettyPrinter(indent=4)
    period = 300

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    session_id = anomaly["session_id"]

    plot_qoes_for_anomaly(session_id, anomaly_id)
    plot_network_lats_for_anomaly(session_id, anomaly_id, agent="azure")
    plot_session_lat_for_anomaly(session_id, anomaly_id)


    #session = get_objects(datafolder+session_file, [session_id])[0]
    # pp.pprint(session)
    # session_qoes = get_session_qoes_in_range(qoesfolder, session_id, draw_start, draw_end)

    #img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_qoes"

    #network_ids = get_networks_by_session(session)
    # pp.pprint(network_ids)


