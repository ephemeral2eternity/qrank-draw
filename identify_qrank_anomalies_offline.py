from json_utils import *
from data_folder import *

##########################################################################################################
## @descr: Get the anomaly ratio from a dictionary of session status
## @params: related_session_status ---- a dictionary contains session ids as keys and session status as values.
## @return: anomaly_ratio ---- the ratio of anomaly sessions in related_session_status
##########################################################################################################
def get_anomaly_ratio(related_session_status):
    total_sessions = 0
    anomaly_sessions = 0
    for session_id in related_session_status:
        if not related_session_status[session_id]:
            anomaly_sessions += 1
        total_sessions += 1
    anomaly_ratio = anomaly_sessions / float(total_sessions)
    return anomaly_ratio

##########################################################################################################
## @descr: Get the anomaly system by ranking the anomaly ratio and qoe score among suspect systems
## @params: suspect_systems ---- a list of suspect systems detected
## @return: anomaly_systems ---- a list of anomaly systems with maximum anomaly ratio and minimum QoE score.
##########################################################################################################
def rank_suspect_systems(suspect_systems):
    suspect_systems_dict = {}
    suspect_systems_qoe_dict = {}
    suspect_systems_anomaly_ratio_dict = {}
    suspect_system_id = 0
    for suspect_sys in suspect_systems:
        suspect_systems_dict[suspect_system_id] = suspect_sys
        suspect_systems_qoe_dict[suspect_system_id] = suspect_sys["qoe_score"]
        suspect_systems_anomaly_ratio_dict[suspect_system_id] = get_anomaly_ratio(suspect_sys["session_status"])
        suspect_system_id += 1

    max_sys_ids = [k for k, v in suspect_systems_anomaly_ratio_dict.iteritems() if v == max(suspect_systems_anomaly_ratio_dict.values())]

    top_suspect_systems_qoes = {}
    for sys_id in max_sys_ids:
        top_suspect_systems_qoes[sys_id] = suspect_systems_qoe_dict[sys_id]

    anomaly_sys_ids = [k for k, v in top_suspect_systems_qoes.iteritems() if v == min(top_suspect_systems_qoes.values())]

    anomaly_systems = []
    for anomaly_sys_id in anomaly_sys_ids:
        anomaly_systems.append(suspect_systems_dict[anomaly_sys_id])
    return anomaly_systems


#####################################################################################
## @descr: Identify anomaly system among a list of suspect systems obtained by QRank offline code
## @params: anomalies ---- a dictionary contains keys as session ids and lists of anomalies as values
## @return: dump anomalies per session to qrank folder with anomaly_system added in the anomaly dict.
#####################################################################################
def identifyAnomalySystem(anomalies):
    for session_id in anomalies:
        session_anomalies = []
        for anomaly in anomalies[session_id]:
            suspect_systems = anomaly["qrank"]
            anomaly_system = rank_suspect_systems(suspect_systems)
            anomaly["anomaly_system"] = anomaly_system
            session_anomalies.append(anomaly)
        dumpJson(session_anomalies, qrankfolder + "session_" + str(session_id) + "_anomalies.json")

if __name__ == '__main__':
    # datafolder = "/Users/chenw/Data/QRank/20170510/"
    # anomaly_file = "merged_anomalies_revised.json"      ## revised file remove the dallas client that is bad all the time
    anomaly_file = "qrank_anomalies.json"
    ## Read anomalies after merging
    anomalies = loadJson(datafolder + anomaly_file)
    identifyAnomalySystem(anomalies)