from json_utils import *
from data_folder import *
import numpy as np

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
## @descr: Get the session object by denoting the session_id.
## @params: session_id ---- the id of the session to get the anomaly
## @return: session ---- the session object that contains the details of a session
#####################################################################################
def get_session(session_id):
    session = get_objects(datafolder + session_file, [session_id])[0]
    return session

#####################################################################################
## @descr: Get the total number of sessions
## @return: session_num ---- the total number of available sessions
#####################################################################################
def count_total_sessions():
    sessions = loadJson(datafolder+session_file)
    session_num = len(sessions.keys())
    return session_num

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
        cur_link_obj = {"src":src_node["ip"], "dst":dst_node["ip"], "srcNet":src_net["as"], "dstNet":dst_net["as"]}
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
## @descr: get a session's QoE status during a time window
## @params: session_id ---- the id of the session to get the QoE status
##          startTS ---- The start timestamp of the time range
##          endTS ---- The end timestamp of the time range
## @return: True ---- The session has good QoE and no QoE anomalies.
##          False ---- The session has bad QoE and had QoE anomalies.
#####################################################################################
def get_session_status_in_range(session_id, startTS, endTS):
    session_qoe_file = qoesfolder + "session_" + str(session_id) + "_qoes.json"
    session_qoes = loadJson(session_qoe_file)
    session_qoes_list = session_qoes["qoes"]
    qoes_to_get = []
    for qoe in session_qoes_list:
        if (float(qoe["timestamp"]) >= startTS) and (float(qoe["timestamp"]) < endTS) and (float(qoe["QoE"]) < qoe_th):
            return False

    return True

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
