import json
from json_utils import *

qoe_th = 2
intvl_th = 12
intvl_seconds_th = 60

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
        return merged_anomaly
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
        return merged_anomaly

#####################################################################################
## @descr: merge continous anomalies as one long anomaly and update the start and end timestamp.
## @params: session_qoes ---- all qoes on one session
##          session_anomalies ---- all raw anomalies data on the session
## @return: all anomalies after merging.
#####################################################################################
def merge_anomalies(session_qoes, session_anomalies):
    anomaly_periods = search_anomaly_period(session_qoes)
    merged_session_anomalies = []
    for one_period in anomaly_periods:
        start_ts = one_period[0]
        end_ts = one_period[1]
        merged_anomaly = merge_anomalies_within_period(session_anomalies, start_ts, end_ts)
        if merged_anomaly:
            merged_session_anomalies.append(merged_anomaly)

    return merged_session_anomalies

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
    for session_id, session_anomalies in sessions_anomalies.iteritems():
        session_qoes_file = datafolder + "sessions//qoes//session_" + str(session_id) + "_qoes.json"
        session_qoes = loadJson(session_qoes_file)
        merged_session_anomalies = merge_anomalies(session_qoes, session_anomalies)
        all_session_anomalies[session_id] = merged_session_anomalies

    return all_session_anomalies


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



if __name__ == '__main__':
    # datafolder = "D://Data//QRank//20170510//"
    datafolder = "/Users/chenw/Data/QRank/20170610/"
    anomaly_file = "anomalies.json"


    anomalies = loadJson(datafolder+anomaly_file)
    processedAnomalies = processAnomalies(datafolder, anomalies)
    dumpJson(processedAnomalies, datafolder + "merged_anomalies_complete.json")

    '''
    sessions_anomalies = getAnomaliesPerSession(anomalies)
    #dumpJson(session_anomalies, datafolder + "session_anomalies.json")

    session_anomalies = sessions_anomalies[83]
    session_qoes_file = datafolder + "sessions//qoes//session_" + str(83) + "_qoes.json"
    session_qoes = loadJson(session_qoes_file)

    session_merged_anomalies = merge_anomalies(session_qoes, session_anomalies)
    # print(session_merged_anomalies)
    '''