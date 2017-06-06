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
# datafolder = "D:/Data/QRank/20170510/"
datafolder = "/Users/chenw/Data/QRank/20170510/"

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

#####################################################################################
## @descr: Get the anomaly object by denoting the anomaly_id and the session_id the
## anomaly is on.
## @params: session_id ---- the id of the session to get the anomaly
##          anomaly_id ---- the id of the anomaly
## @return: anomaly ---- the anomaly object that contains the details of the anomaly
#####################################################################################
def get_objects(all_object_file, object_ids):
    all_objects = loadJson(all_object_file)
    objects = [all_objects[str(x)] for x in object_ids]
    return objects


#####################################################################################
## @descr: Get the anomaly object by denoting the anomaly_id and the session_id the
## anomaly is on.
## @params: session_id ---- the id of the session to get the anomaly
##          anomaly_id ---- the id of the anomaly
## @return: anomaly ---- the anomaly object that contains the details of the anomaly
#####################################################################################
def get_anomaly(session_id, anomaly_id):
    all_session_anomalies = loadJson(datafolder + anomaly_file)
    session_anomalies = all_session_anomalies[str(session_id)]
    for anomaly in session_anomalies:
        if int(anomaly["id"]) == anomaly_id:
            return anomaly
    return None

#####################################################################################
## @descr: Get the link details from the list of link objects
## @params: session_id ---- the id of the session to get the anomaly
##          anomaly_id ---- the id of the anomaly
## @return: link_details ---- the dictionary of link details
## {link_id: { src: src_ip, dst:dst_ip, srcNet:src_net_name, dstNet:dst_net_name}}
#####################################################################################
def get_link_details(link_objs):
    link_details = {}
    for link_id in link_objs.keys():
        src_node_id = link_objs[link_id]["src"]
        src_node = get_node(src_node_id)
        src_net = get_network(src_node["network"])
        dst_node_id = link_objs[link_id]["dst"]
        dst_node = get_node(dst_node_id)
        dst_net = get_network(dst_node["network"])
        cur_link_obj = {"src":src_node["ip"], "dst":dst_node["ip"], "srcNet":src_net["name"], "dstNet":dst_net["name"]}
        link_details[link_id] = cur_link_obj
    return link_details

#####################################################################################
## @descr: Get the link latencies from the list of link ids in a time range
## @params: startTS ---- The start timestamp of the time range
##          endTS ---- The end timestamp of the time range
## @return: link_lats ---- the dictionary of link latencies list
## {link_id: { src: src_ip, dst:dst_ip, srcNet:src_net_name, dstNet:dst_net_name}}
#####################################################################################
def get_link_lats_in_range(link_ids, startTS, endTS):
    all_links_lats = {}
    for link_id in link_ids:
        link_lats = loadJson(linksfolder + "link_" + str(link_id) + "_lats.json")
        cur_link_lats = []
        for ts in link_lats.keys():
            if (float(ts) >= startTS) and (float(ts) < endTS):
                cur_link_lats.append({"timestamp":float(ts), "latency":link_lats[ts]})
        all_links_lats[link_id] = cur_link_lats
    return all_links_lats

#####################################################################################
## @descr: Get session QoEs from a session within a time range
## @params: session_id ---- the id of the session to get the latencies
##          startTS ---- The start timestamp of the time range
##          endTS ---- The end timestamp of the time range
## @return: the qoe list within the time range for the session
#####################################################################################
def get_session_qoes_in_range(session_id, startTS, endTS):
    session_qoe_file = qoesfolder + "session_" + str(session_id) + "_qoes.json"
    session_qoes = loadJson(session_qoe_file)
    session_qoes_list = session_qoes["qoes"]
    qoes_to_get = []
    for qoe in session_qoes_list:
        if (float(qoe["timestamp"]) >= startTS) and (float(qoe["timestamp"]) < endTS):
            qoes_to_get.append({"timestamp":float(qoe["timestamp"]),"QoE":float(qoe["QoE"])})

    return qoes_to_get

#####################################################################################
## @descr: get session latencies in a timestamp range
## @params: session_id ---- the id of the session to get the latencies
##          startTS ---- The start timestamp of the time range
##          endTS ---- The end timestamp of the time range
## @return: the latencies list within the range for the session
#####################################################################################
def get_session_lats_in_range(session_id, startTS, endTS):
    session_lats_file = latsfolder + "session_" + str(session_id) + "_lats.json"
    session_lats = loadJson(session_lats_file)
    lats_to_get = []
    for ts in session_lats.keys():
        if (float(ts) >= startTS) and (float(ts) < endTS):
            lats_to_get.append({"timestamp":float(ts),"latency":float(session_lats[ts])})

    return lats_to_get

#####################################################################################
## @descr: compute the mean and std of all latencies and for latencies within the denoted anomaly period
## @params: lats ---- latency list with all latency objects to study
##          anomalyStart ---- The start timestamp of the anomalous period
##          anomalyEnd ---- The end timestamp of the anomalous period
## @return: {"all_lat_mn": all_lat_mn, "all_lat_std": all_lat_std,
##           "anomaly_lat_mn":anomaly_lat_mn, "anomaly_lat_std":anomaly_lat_std}
#####################################################################################
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

#####################################################################################
## @descr: Get the node info by the node id
## @params: node_id ---- The id of the node to obtain node info
## @return: node --- details of the node
#####################################################################################
def get_node(node_id):
    all_nodes_info = loadJson(datafolder + node_file)
    node = all_nodes_info[str(node_id)]
    return node

#####################################################################################
## @descr: Get network ids for all networks involved in a session
## @params: session --- the session to get networks
## @return: unique_network_ids --- unique network ids involved in the given session
#####################################################################################
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

#####################################################################################
## @descr: Get the network info json by the network id
## @params: network_id --- the id of the network to be requested
## @return: network --- the network object
#####################################################################################
def get_network(network_id):
    networks = loadJson(datafolder + network_file)
    network = networks[str(network_id)]
    return network

#####################################################################################
## @descr: Get the network info json by the network id
## @params: network_id --- the id of the network to be requested
## @return: cur_network_lats_in_range --- the network probed latencies within
##  the denoted time range
#####################################################################################
def get_network_lats_in_range(network_id, startTS, endTS, agent="planetlab"):
    network_lats = loadJson(networksfolder + "network_" + str(network_id) + "_lats.json")
    lats_json = network_lats[agent]
    cur_network_lats_in_range = []
    for ts in lats_json.keys():
        if (float(ts) >= startTS) and (float(ts) <= endTS) and (lats_json[ts] > 0):
            cur_network_lats_in_range.append({"timestamp":float(ts), "latency":lats_json[ts]})
    return cur_network_lats_in_range

#####################################################################################
## @descr: Plot the qoes values within an anomaly period
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the anomalous period
#####################################################################################
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

#####################################################################################
## @descr: Plot the probed latencies for all networks involved in a session in
##         an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
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

#####################################################################################
## @descr: Plot the latencies probed by traceroute for all links in a session
##         within an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_link_lats_for_anomaly(session_id, anomaly_id):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    link_objs = session["links"]
    link_ids = link_objs.keys()

    link_details = get_link_details(link_objs)
    link_lats = get_link_lats_in_range(link_ids, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_lats"



#####################################################################################
## @descr: Plot the session latencies in an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
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
    plot_network_lats_for_anomaly(session_id, anomaly_id, agent="planetlab")
    plot_link_lats_for_anomaly(session_id, anomaly_id)
    plot_session_lat_for_anomaly(session_id, anomaly_id)


    #session = get_objects(datafolder+session_file, [session_id])[0]
    # pp.pprint(session)
    # session_qoes = get_session_qoes_in_range(qoesfolder, session_id, draw_start, draw_end)

    #img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_qoes"

    #network_ids = get_networks_by_session(session)
    # pp.pprint(network_ids)


