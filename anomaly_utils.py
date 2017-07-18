import json
from json_utils import *
from data_folder import *
from get_objects import *

#####################################################################################
## @descr: Classify the severity of the anomaly according to the percentage of poor QoE during the
## anomaly period
## @params: session_qoes ---- all qoes on the session with anomaly
##          anomaly ---- the anomaly to be classified
## @return: the type of the anomaly: 1: light, 2: medium, 3:severe
#####################################################################################
def classifyAnomaly(anomaly, session_qoes):
    start_ts = anomaly["start"]
    end_ts = anomaly["end"]
    total_cnt = 0
    poor_qoe_cnt = 0
    for qoe_obj in session_qoes:
        if (float(qoe_obj["timestamp"]) <= end_ts) and (float(qoe_obj["timestamp"]) >= start_ts):
            total_cnt += 1
            if float(qoe_obj["QoE"]) <= qoe_th:
                poor_qoe_cnt += 1

    poor_percent = float(poor_qoe_cnt) / float(total_cnt)
    if poor_percent < 0.2:
        ## Return "light" anomaly
        return "light"
    elif poor_percent < 0.7:
        ## Return "medium" anomaly
        return "medium"
    else:
        ## Return "severe" anomaly
        return "severe"

#####################################################################################
## @descr: Going through all qoes on one session and obtain the start and end timestamp
## of all QoE anomalies. Chunk QoEs violating SLA within 1 minute are grouped as one anomaly.
## @params: session_qoes ---- all qoes on one session
## @return: anomaly_period ---- the start and end timestamps of all QoE anomalies on the session
#####################################################################################
def search_anomaly_period(session_qoes):
    anomaly_start = False
    anomaly_intvl = 0

    anomaly_period = []

    anomaly_qoes = []
    session_qoes_list = session_qoes["qoes"]
    for qoe_obj in session_qoes_list:
        ts = qoe_obj["timestamp"]
        qoe = float(qoe_obj["QoE"])
        if anomaly_start:
            anomaly_qoes.append(qoe_obj)

            if (anomaly_intvl > intvl_th) or (ts - latest_anomaly_ts > intvl_seconds_th):
                anomaly_end_ts = latest_anomaly_ts
                # print("QoE values within anomaly period:")
                if anomaly_end_ts == anomaly_start_ts:
                    anomaly_end_ts = anomaly_end_ts + 5.0
                    #print(anomaly_qoes[0])
                #else:
                    #print(anomaly_qoes)

                print("Detects anomaly from %.2f to %.2f" % (anomaly_start_ts, anomaly_end_ts))
                anomaly_period.append([anomaly_start_ts, anomaly_end_ts])
                anomaly_start = False
                anomaly_qoes = []

            if qoe < qoe_th:
                anomaly_intvl = 0
                latest_anomaly_ts = ts
            else:
                anomaly_intvl += 1

        else:
            if qoe < qoe_th:
                anomaly_start = True
                anomaly_start_ts = ts
                latest_anomaly_ts = ts
                anomaly_qoes.append(qoe_obj)

    return anomaly_period

#####################################################################################
## @descr: Given the start and end timestamp of one anomalies, search all detected raw anomalies
##         and merge those into one anomaly.
## @params: session_anomalies ---- all raw anomalies data on the session
##          start_ts ---- the starting timestamp of the anomaly
##          end_ts ---- the ending timestamp of the anomaly
## @return: updated anomaly after merging.
#####################################################################################
def merge_anomalies_within_period(session_anomalies, start_ts, end_ts):
    anomalies_in_period = {}
    anomalies_in_period_origin_cnt = {}
    for anomaly_id, anomaly in session_anomalies.iteritems():
        if (anomaly["timestamp"] >= start_ts) and (anomaly["timestamp"] <= end_ts):
            anomalies_in_period[anomaly_id] = anomaly
            anomalies_in_period_origin_cnt[anomaly_id] = len(anomaly["origins"])

    if anomalies_in_period:
        merged_anomaly_id = min(anomalies_in_period_origin_cnt.items(), key=lambda x:x[1])[0]
        merged_anomaly = anomalies_in_period[merged_anomaly_id]
        merged_anomaly["start"] = start_ts
        merged_anomaly["end"] = end_ts
        merged_anomaly["id"] = merged_anomaly_id
    else:
        merged_anomaly = {}
        merged_anomaly["start"] = start_ts
        merged_anomaly["end"] = end_ts
        merged_anomaly["origins"] = "unknown"
        if session_anomalies:
            first_obj = session_anomalies[session_anomalies.keys()[0]]
            merged_anomaly["locator"] = first_obj["locator"]
            merged_anomaly["session_id"] = first_obj["session_id"]
            merged_anomaly["session_lid"] = first_obj["session_lid"]

    return  merged_anomaly

#####################################################################################
## @descr: merge continous anomalies as one long anomaly and update the start and end timestamp.
## @params: session_qoes ---- all qoes on one session
##          session_anomalies ---- all raw anomalies data on the session
## @return: all anomalies after merging.
#####################################################################################
def merge_anomalies(session_qoes, session_anomalies):
    anomaly_periods = search_anomaly_period(session_qoes)
    merged_session_anomalies = []
    merged_session_anomalies_complete = []
    for one_period in anomaly_periods:
        start_ts = one_period[0]
        end_ts = one_period[1]
        merged_anomaly = merge_anomalies_within_period(session_anomalies, start_ts, end_ts)
        anomaly_type = classifyAnomaly(merged_anomaly, session_qoes["qoes"])
        merged_anomaly["type"] = anomaly_type
        if merged_anomaly:
            if merged_anomaly["origins"] != "unknown":
                merged_session_anomalies.append(merged_anomaly)
            merged_session_anomalies_complete.append(merged_anomaly)

    return merged_session_anomalies, merged_session_anomalies_complete

#####################################################################################
## @descr: process per session anomalies data to merge continuous anomalies and retrieve
## anomalous period according to QoE updates
## @params: anomalies ---- raw anomalies data that list anomalies by id, those anomalies
## are raw data that are detected per minute and are diagnosed per minute
## @return: processed_anomalies ---- json data that list anomalies per session including
## the start and end time of the anomaly. Those anomalies data are processed data that estimate
## anomalous period according to QoE and continous anomalies are already concatenated as one anomaly.
#####################################################################################
def processAnomalies(dataFolder, anomalies):
    sessions_anomalies = getAnomaliesPerSession(anomalies)
    all_session_anomalies = {}
    all_session_anomalies_complete = {}
    for session_id, session_anomalies in sessions_anomalies.iteritems():
        session_qoes_file = datafolder + "sessions//qoes//session_" + str(session_id) + "_qoes.json"
        session_qoes = loadJson(session_qoes_file)
        merged_session_anomalies, merged_session_anomalies_complete = merge_anomalies(session_qoes, session_anomalies)
        all_session_anomalies_complete[session_id] = merged_session_anomalies_complete
        all_session_anomalies[session_id] = merged_session_anomalies

    return all_session_anomalies, all_session_anomalies_complete


#####################################################################################
## @descr: concatenate all anomalies per session
## @params: anomalies ---- raw anomalies data that list anomalies by id
## @return: session_anomalies ---- json data that list anomalies per session
#####################################################################################
def getAnomaliesPerSession(anomalies):
    sessions_anomalies = {}
    for anomaly_id, anomaly in anomalies.iteritems():
        if anomaly["session_id"] not in sessions_anomalies.keys():
            sessions_anomalies[anomaly["session_id"]] = {}

        sessions_anomalies[anomaly["session_id"]][anomaly_id] = anomaly

    return sessions_anomalies

#######################################################################################################
## @descr: get all related session ids for a session, which is prepared for QRank anomaly identification
## @params: session_id ---- the session id to retrieve the related session ids
## @return: related_session_ids ---- the list of ids that are related to the current session
##          session_node_details ---- the details of all nodes in this session
#######################################################################################################
def get_related_sessions(session_id):
    session_details = get_session(session_id)

    related_session_ids = []
    session_node_details = {}
    hops = session_details["hops"]
    for hop_id in hops:
        hop_nodes = hops[hop_id]
        for node_id in hop_nodes:
            if node_id not in session_node_details.keys():
                session_node_details[node_id] = get_node(node_id)
                cur_related_session = session_node_details[node_id]["related_sessions"]
                related_session_ids = related_session_ids + list(set(cur_related_session) - set(related_session_ids))

    return related_session_ids, session_node_details

#######################################################################################################
## @descr: locate all suspect nodes for an anomaly (QWatch system emulation)
## @params: anomaly ---- the anomaly to locate the suspect nodes that are exclusively on its session's path
## @return: suspect_nodes ---- the list of suspect node objects that are exclusively
# on the path of the session that has the anomaly.
#######################################################################################################
def locate_suspect_nodes(anomaly):
    related_session_ids, session_node_details = get_related_sessions(anomaly["session_id"])
    anomaly_start = anomaly["start"]
    anomaly_end = anomaly["end"]
    anomaly_period = anomaly_end - anomaly_start

    cur_ts = anomaly_start

    min_suspect_nodes = session_node_details.keys()
    while cur_ts < anomaly_end:
        suspect_nodes = []
        if cur_ts + locate_time_window < anomaly_end:
            cur_end = cur_ts + locate_time_window
        else:
            cur_end = anomaly_end
        for node_id in session_node_details:
            node_related_sessions = session_node_details[node_id]["related_sessions"]
            node_suspect = True
            for related_session in node_related_sessions:
                if related_session != anomaly["session_id"]:
                    related_session_status = get_session_status_in_range(related_session, cur_ts, cur_ts + locate_time_window)
                    if related_session_status:
                        node_suspect = False
                        break
            if node_suspect:
                suspect_nodes.append(node_id)
        cur_ts = cur_end
        if len(suspect_nodes) < len(min_suspect_nodes):
            min_suspect_nodes = suspect_nodes

    suspect_node_details = []
    for suspect_node_id in min_suspect_nodes:
        suspect_node_details.append(session_node_details[suspect_node_id])

    return suspect_node_details

#####################################################################################
## @descr: retrieves the suspect systems from the suspect nodes
## @params: suspect_nodes ---- located suspect nodes from qwatch
## @return: suspect systems ---- device, networks, server
#####################################################################################
def retrieve_suspect_systems(suspect_nodes):
    added_nets = []
    suspect_systems = []
    for node in suspect_nodes:
        if node["type"] == "client":
            node_device = get_device(node["ip"])
            suspect_system = {"type": "device", "obj":node_device}
            suspect_systems.append(suspect_system)
        elif node["type"] == "server":
            suspect_system = {"type": "server", "obj":node}
            suspect_systems.append(suspect_system)
        else:
            if node["network"] not in added_nets:
                added_nets.append(node["network"])
                network = get_network(node["network"])
                suspect_system = {"type": "network", "obj": network}
                suspect_systems.append(suspect_system)

    return suspect_systems


#####################################################################################
## @descr: offline qrank for all anomalies detected
## @params: anomaly ---- one raw anomaly data that contains the start and the end of the anomaly
## @return: anomaly_details
#####################################################################################
def qrank_identify_anomaly(anomaly):
    suspect_nodes = locate_suspect_nodes(anomaly)
    suspect_systems = retrieve_suspect_systems(suspect_nodes)
    # ranked_anomaly_systems = ranking_suspect_systems(suspect_systems)
    # return ranked_anomaly_systems


if __name__ == '__main__':
    datafolder = "D://Data//QRank//20170712//"
    # datafolder = "/Users/chenw/Data/QRank/20170610/"
    # anomaly_file = "anomalies.json"
    anomaly_file = "merged_anomalies_complete.json"

    anomalies = loadJson(datafolder+anomaly_file)

    for session_id, session_anomalies in anomalies.iteritems():
        for anomaly in session_anomalies:
            qrank_identify_anomaly(anomaly)

    '''
    processedAnomalies, processedAnomaliesComplete = processAnomalies(datafolder, anomalies)
    dumpJson(processedAnomalies, datafolder + "merged_anomalies.json")
    dumpJson(processedAnomaliesComplete, datafolder + "merged_anomalies_complete.json")
    '''

    '''
    sessions_anomalies = getAnomaliesPerSession(anomalies)
    #dumpJson(session_anomalies, datafolder + "session_anomalies.json")

    session_anomalies = sessions_anomalies[83]
    session_qoes_file = datafolder + "sessions//qoes//session_" + str(83) + "_qoes.json"
    session_qoes = loadJson(session_qoes_file)

    session_merged_anomalies = merge_anomalies(session_qoes, session_anomalies)
    # print(session_merged_anomalies)
    '''