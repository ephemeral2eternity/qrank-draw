import glob
import os
import re
from data_folder import *
from get_objects import *

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
        for anomaly in session_anomalies:
            anomaly_type = classifyAnomaly(anomaly, session_qoes)
            anomaly["type"] = anomaly_type
            updated_session_anomalies.append(anomaly)

        dumpJson(updated_session_anomalies, session_file)

    return anomalous_sessions


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
def get_anomalous_sessions():
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
## @descr: Get the anomaly statistics per session
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def get_anomalies_stats_per_session(anomalies):
    anomalies_per_session = []
    session_anomalies = get_anomalous_sessions()
    for session_id, session_details in session_anomalies.iteritems():
        session_anomalies = session_details["anomalies"]
        session_dict = {"session":session_id, "user":session_details["client"]}
        cnt = {"severe":0, "medium":0, "light":0, "total":len(session_anomalies)}
        period = {"severe":0, "medium":0, "light":0, "total":0}
        for anomaly in session_anomalies:
            anomaly_type = anomaly["type"]
            anomaly_period = float(anomaly["end"]) - float(anomaly["start"])
            cnt[anomaly_type] += 1
            period[anomaly_type] += anomaly_period
            period["total"] += anomaly_period

        for a_type in period.keys():
            if cnt[a_type] > 0:
                period[a_type] = period[a_type] / float(cnt[a_type])
            session_dict[a_type + "_count"] = cnt[a_type]
            session_dict[a_type + "_ave_period"] = period[a_type]

        anomalies_per_session.append(session_dict)

    return anomalies_per_session

#####################################################################################
## @descr: analyze QoE anomalies from all sessions
## that locates the anomalies over the origin type
#####################################################################################
if __name__ == '__main__':
    ## Get the # of anomalous sessions from PlanetLab users
    classifyAllSessionAnomalies()

    #anomalous_sessions = get_anomalous_sessions()
    #anomalous_session_cnt = len(anomalous_sessions.keys())
    #print("There are totall %d anomalous sessions!" % anomalous_session_cnt)