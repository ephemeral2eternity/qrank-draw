import glob
import os
import re
from data_folder import *
from get_objects import *
from get_address import *
from get_asname import *
import numpy as np
import pprint

#####################################################################################
## @descr: Classify the severity of all QoE anomalies per session
## @return: update the session anomaly file in qrankfolder
#####################################################################################
def classifyAllSessionAnomalies():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_file)
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_qoes_file = datafolder + "sessions//qoes//session_" + str(session_id) + "_qoes.json"
        session_qoes = loadJson(session_qoes_file)
        updated_session_anomalies = []
        print("Updating anomaly type for anomalies on session : %d" % int(session_id))
        for anomaly in session_anomalies:
            anomaly_type = classifyAnomaly(anomaly, session_qoes["qoes"])
            anomaly["type"] = anomaly_type
            updated_session_anomalies.append(anomaly)

        dumpJson(updated_session_anomalies, session_file)

    return anomalous_sessions

#####################################################################################
## @descr: Cut all anomalies if its duration is longer than a whole session long period, 3600 seconds
## @return: update the session anomaly file in qrankfolder
#####################################################################################
def cutAllSessionAnomalies():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_file)
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        updated_session_anomalies = []
        print("Updating anomaly type for anomalies on session : %d" % int(session_id))
        for anomaly in session_anomalies:
            org_start = anomaly["start"]
            org_end = anomaly["end"]
            org_duration = org_end - org_start
            print("The original anomaly duration is %d seconds!" % org_duration)
            if org_duration > max_anomaly_duration:
                cur_start = org_start
                cur_end = cur_start + max_anomaly_duration
                while cur_start < org_end:
                    new_anomaly = anomaly
                    if cur_start + max_anomaly_duration > org_end:
                        cur_end = org_end
                    else:
                        cur_end = cur_start + max_anomaly_duration
                    new_anomaly["start"] = cur_start
                    new_anomaly["end"] =  cur_end
                    updated_session_anomalies.append(new_anomaly)
                    print("The updated anomaly duration is %d seconds!" % (cur_end - cur_start))
                    cur_start = cur_end + 1
            else:
                updated_session_anomalies.append(anomaly)
                print("No need to cut the anomaly as the duration is less than the maximum duration %d" % max_anomaly_duration)
        dumpJson(updated_session_anomalies, session_file)

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
## @descr: load QoE anomalies per session
#####################################################################################
def get_all_anomalous_sessions():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_obj = get_session(session_id)
        server = get_node(session_obj["server"])
        client = get_node(session_obj["client"])
        anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"]}
        session_anomalies = loadJson(session_file)
        anomalous_sessions[session_id]["anomalies"] = session_anomalies
    return anomalous_sessions

#####################################################################################
## @descr: get sessions with certain type of QoE anomalies
#####################################################################################
def get_persistent_anomalous_sessions():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    persistent_anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_obj = get_session(session_id)
        server = get_node(session_obj["server"])
        client = get_node(session_obj["client"])
        #anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"]}
        session_anomalies = loadJson(session_file)
        isPersistent = False
        long_anomalies = []
        # anomalous_sessions[session_id][anomaly_type] = session_anomalies
        for anomaly in session_anomalies:
            anomaly_duration = anomaly["end"] - anomaly["start"]
            if anomaly_duration > persistent_anomaly_len_th:
                long_anomalies.append(anomaly)
                isPersistent = True
                # break

        if isPersistent:
            persistent_anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"], "anomalies": long_anomalies}

    dumpJson(persistent_anomalous_sessions, datafolder  + "persistent_session_anomalies.json")
    return persistent_anomalous_sessions

#####################################################################################
## @descr: get sessions with certain type of QoE anomalies
#####################################################################################
def get_recurrent_anomalous_sessions():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    recurrent_anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_obj = get_session(session_id)
        server = get_node(session_obj["server"])
        client = get_node(session_obj["client"])
        #anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"]}
        session_anomalies = loadJson(session_file)
        short_anomalies = []
        # anomalous_sessions[session_id][anomaly_type] = session_anomalies
        for anomaly in session_anomalies:
            anomaly_duration = anomaly["end"] - anomaly["start"]
            if anomaly_duration <= persistent_anomaly_len_th:
                short_anomalies.append(anomaly)

        if len(short_anomalies) > recurrent_cnt_th:
            recurrent_anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"], "anomalies": short_anomalies}

    dumpJson(recurrent_anomalous_sessions, datafolder  + "recurrent_session_anomalies.json")
    return recurrent_anomalous_sessions

#####################################################################################
## @descr: get sessions with certain type of QoE anomalies
#####################################################################################
def get_occasional_anomalous_sessions():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    occasional_anomalous_sessions = {}
    for session_file in all_session_anomaly_files:
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_obj = get_session(session_id)
        server = get_node(session_obj["server"])
        client = get_node(session_obj["client"])
        #anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"]}
        session_anomalies = loadJson(session_file)
        short_anomalies = []
        isOccasional = True
        # anomalous_sessions[session_id][anomaly_type] = session_anomalies
        for anomaly in session_anomalies:
            anomaly_duration = anomaly["end"] - anomaly["start"]
            if anomaly_duration <= persistent_anomaly_len_th:
                short_anomalies.append(anomaly)

        if len(short_anomalies) > recurrent_cnt_th:
            isOccasional = False

        if isOccasional:
            occasional_anomalous_sessions[session_id] = {"server": server["name"], "client": client["name"], "anomalies": short_anomalies}

    dumpJson(occasional_anomalous_sessions, datafolder  + "occasional_session_anomalies.json")
    return occasional_anomalous_sessions

#####################################################################################
## @descr: Get the anomaly statistics per session
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def get_anomalies_stats_per_session(session_anomalies):
    anomalies_per_session = []
    for session_id, session_details in session_anomalies.iteritems():
        session_anomalies = session_details["anomalies"]
        session_dict = {"session":session_id, "user":session_details["client"]}
        anomaly_period_per_type = {"severe":[], "medium":[], "light":[], "total":[]}
        cur_session_anomaly_period = []
        for anomaly in session_anomalies:
            anomaly_type = anomaly["type"]
            anomaly_period = float(anomaly["end"]) - float(anomaly["start"])
            anomaly_period_per_type[anomaly_type].append(anomaly_period)
            anomaly_period_per_type["total"].append(anomaly_period)

        for a_type in anomaly_period_per_type.keys():
            session_dict[a_type + "_count"] = len(anomaly_period_per_type[a_type])
            session_dict[a_type + "_ave_period"] = np.mean(anomaly_period_per_type[a_type])

        anomalies_per_session.append(session_dict)

    return anomalies_per_session

#####################################################################################
## @descr: Get the statistics of anomalies in a list
## @params: anomaly_list
## @return: the count and the average period of all anomalies in the list
#####################################################################################
def get_anomaly_stats(anomaly_list):
    all_anomaly_duration = []
    for anomaly in anomaly_list:
        anomaly_duration = float(anomaly["end"] - anomaly["start"])
        all_anomaly_duration.append(anomaly_duration)

    all_anomaly_count = len(all_anomaly_duration)
    ave_anomaly_duration = np.mean(all_anomaly_duration)
    return all_anomaly_count, ave_anomaly_duration

#####################################################################################
## @descr: Get the anomalies within each anomaly origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################
def get_anomalies_per_origin_type(session_anomalies):
    per_origin_anomalies = {"network": [], "access_network": [], "transit_network": [], "cloud_network": [], "server": [], "device": []}
    for session_id, session_details in session_anomalies.iteritems():
        session_anomalies = session_details["anomalies"]

        for anomaly in session_anomalies:
            anomalous_systems = anomaly["anomaly_system"]
            all_anomalous_system_types = []
            for anomalous_sys in anomalous_systems:
                if anomalous_sys["type"] == "network":
                    if "network" not in all_anomalous_system_types:
                        all_anomalous_system_types.append("network")
                    network_type = anomalous_sys["obj"]["type"]
                    anomalous_sys_type = network_type + "_network"
                else:
                    anomalous_sys_type = anomalous_sys["type"]

                if anomalous_sys_type not in all_anomalous_system_types:
                    all_anomalous_system_types.append(anomalous_sys_type)

            for origin in all_anomalous_system_types:
                per_origin_anomalies[origin].append(anomaly)

    return per_origin_anomalies


#####################################################################################
## @descr: Get the anomalies within each anomaly origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################
def get_anomaly_stats_per_origin_type(session_anomalies):
    anomalies_per_origin_type = get_anomalies_per_origin_type(session_anomalies)
    anomalies_stats_per_origin_type = {}
    for origin_type in anomalies_per_origin_type.keys():
        total_cnt, ave_duration = get_anomaly_stats(anomalies_per_origin_type[origin_type])
        anomalies_stats_per_origin_type[origin_type] = {"total_count":total_cnt, "ave_duration":ave_duration}

    return anomalies_stats_per_origin_type


#####################################################################################
## @descr: Get the anomalies stats per origin type over all origins
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
##          graph ---- "cloud_network", "transit_network", "access_network", "device", "server"
## @return: data_to_draw ---- the data to draw
#####################################################################################
def get_anomalies_stats_per_specific_origin_type(session_anomalies, origin_typ="access_network"):
    anomalies_per_origin_type = get_anomalies_per_origin_type(session_anomalies)
    anomalies_to_study = anomalies_per_origin_type[origin_typ]

    anomalies_per_origins = {}
    networks_to_save = []
    for anomaly in anomalies_to_study:
        for origin in anomaly["anomaly_system"]:
            ## Get origin_name and cur_origin_type for current anomaly origin
            if (origin["type"] == "network"):
                origin_net = origin["obj"]
                cur_origin_type = origin_net["type"] + "_network"
                origin_name = "AS" + str(origin_net["as"]) + "@(" + "{:.2f}".format(origin_net["latitude"]) + "," + "{:.2f}".format(origin_net["longitude"]) + ")"
            elif origin["type"] in ["server", "device"]:
                cur_origin_type = origin["type"]
                session = get_session(anomaly["session_id"])
                if cur_origin_type == "server":
                    origin_node_id = session["server"]
                    origin_node = get_node(origin_node_id)
                    origin_name = origin_node["name"]
                else:
                    device_info = get_device_by_session_id(anomaly["session_id"])
                    origin_name = device_info["device"]["device"] + "," + device_info["device"]["os"] + "\n" + device_info["device"]["browser"] + "," + device_info["device"]["player"]
            else:
                cur_origin_type = origin["type"]
                origin_name = origin["data"]

            ## If current anomaly origin is the type of origin to study, append the anomaly under the origin name
            if cur_origin_type == origin_typ:
                if origin_name not in anomalies_per_origins.keys():
                    anomalies_per_origins[origin_name] = []
                anomalies_per_origins[origin_name].append(anomaly)

    anomalies_stats_per_origins = []
    for origin in anomalies_per_origins.keys():
        cur_origin_anomalies = anomalies_per_origins[origin]
        cur_origin_total_cnt, cur_origin_ave_duration = get_anomaly_stats(cur_origin_anomalies)
        anomalies_stats_per_origins.append({"total_count": cur_origin_total_cnt, "ave_duration": cur_origin_ave_duration, "origin_name": origin})

    return anomalies_stats_per_origins

#####################################################################################
## @descr: analyze QoE anomalies from all sessions
## that locates the anomalies over the origin type
#####################################################################################
if __name__ == '__main__':
    ## Update the type of all QoE anomalies
    classifyAllSessionAnomalies()

    ## Update the duration of all QoE anomalies, break the anomaly into 2 if it lasts more than 1 hour
    cutAllSessionAnomalies()

    ## Get the # of anomalous sessions from PlanetLab users
    #anomalous_sessions = get_anomalous_sessions()
    #anomalous_session_cnt = len(anomalous_sessions.keys())
    #print("There are totall %d anomalous sessions!" % anomalous_session_cnt)

    ## Draw the QoE count and average QoE anomaly durations over all anomalous sessions



