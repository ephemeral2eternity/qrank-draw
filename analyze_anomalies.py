from json_utils import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from fig_utils import *

qoe_th = 2

#####################################################################################
## @descr: Classify the anomalies according to their top origin types
## @params: anomalies_cnt_per_session ---- all anomaly statistics per session
## @return: the session # for the type of anomalous sessions: occasional/recurrent/persistent
#####################################################################################
def classify_anomalous_sessions(anomalies_cnt_per_session):
    session_types = {"occasional":[], "recurrent":[], "persistent":[], "others":[]}
    for session_dict in anomalies_cnt_per_session:
        if (session_dict["total_count"] < 50) and (session_dict["total_ave_period"] < 60):
            session_types["occasional"].append(session_dict["session"])
        elif (session_dict["total_count"] >= 50) and (session_dict["total_ave_period"] < 60):
            session_types["recurrent"].append(session_dict["session"])
        elif session_dict["total_ave_period"] >= 60:
            session_types["persistent"].append(session_dict["session"])
        else:
            session_types["others"].append(session_dict["session"])

    print(session_types)
    return session_types

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
        return 1
    elif poor_percent < 0.7:
        ## Return "medium" anomaly
        return 2
    else:
        ## Return "severe" anomaly
        return 3

#####################################################################################
## @descr: Get some statistics about all anomalies
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly  data
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def statsAnomaliesPerType(datafolder, anomalies):
    session_cnts_type_type = {3:0, 2:0, 1:0, 0:len(anomalies.keys())}
    anomaly_cnts_per_type = {3:0, 2:0, 1:0, 0:0}
    anomaly_ave_duration_per_type = {3:0, 2:0, 1:0, 0:0}
    for session_id, session_anomalies in anomalies.iteritems():
        session_qoes_file = datafolder + "sessions//qoes//session_" + str(session_id) + "_qoes.json"
        session_qoes = loadJson(session_qoes_file)

        session_type = 0
        for anomaly in session_anomalies:
            anomaly_type = classifyAnomaly(anomaly, session_qoes["qoes"])
            session_type = max(session_type, anomaly_type)
            anomaly_cnts_per_type[anomaly_type] += 1
            anomaly_cnts_per_type[0] += 1
            anomaly_period = float(anomaly["end"]) - float(anomaly["start"])
            anomaly_ave_duration_per_type[anomaly_type] += anomaly_period
            anomaly_ave_duration_per_type[0] += anomaly_period

        session_cnts_type_type[session_type] += 1

    for ano_type in anomaly_cnts_per_type.keys():
        anomaly_ave_duration_per_type[ano_type] = anomaly_ave_duration_per_type[ano_type] / float(anomaly_cnts_per_type[ano_type])

    anomaly_stats = {"session": session_cnts_type_type, "anomalies":anomaly_cnts_per_type, "duration":anomaly_ave_duration_per_type}
    return anomaly_stats

#####################################################################################
## @descr: Get the anomaly statistics per session
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def get_anomalies_stats_per_session(datafolder, anomalies):
    anomalies_per_session = []
    all_types_str = {0:"total", 1:"light", 2:"medium", 3:"severe"}
    for session_id, session_anomalies in anomalies.iteritems():
        print("Processing anomalies in session: %d" % int(session_id))
        session_qoes_file = datafolder + "sessions//qoes//session_" + str(session_id) + "_qoes.json"
        session_qoes = loadJson(session_qoes_file)
        session_dict = {"session":session_id}
        cnt = {"severe":0, "medium":0, "light":0, "total":len(session_anomalies)}
        period = {"severe":0, "medium":0, "light":0, "total":0}
        for anomaly in session_anomalies:
            anomaly_type = classifyAnomaly(anomaly, session_qoes["qoes"])
            anomaly_period = float(anomaly["end"]) - float(anomaly["start"])
            anomaly_type_str = all_types_str[anomaly_type]
            cnt[anomaly_type_str] += 1
            cnt["total"] += 1
            period[anomaly_type_str] += anomaly_period
            period["total"] += anomaly_period

        for a_type in period.keys():
            if cnt[a_type] > 0:
                period[a_type] = period[a_type] / float(cnt[a_type])
            session_dict[a_type + "_count"] = cnt[a_type]
            session_dict[a_type + "_ave_period"] = period[a_type]

        anomalies_per_session.append(session_dict)

    return anomalies_per_session

#####################################################################################
## @descr: Plot the anomaly stats of each anomalous session in bar graph
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: pdf figures saved in datafolder/imgs
#####################################################################################
def plot_anomalies_per_session(datafolder, anomalies):
    anomalies_per_session = get_anomalies_stats_per_session(datafolder, anomalies)
    dumpJson(anomalies_per_session, datafolder + "anomalies_per_session_cnt.json")

    anomalous_session_types = classify_anomalous_sessions(anomalies_per_session)
    dumpJson(anomalous_session_types, datafolder + "anomalous_session_types.json")

    df = pd.DataFrame(anomalies_per_session)
    sorted_df = df.sort_values(by='total_count', ascending=False)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    sorted_df.plot(x='session', y=['light_count', 'medium_count', 'severe_count'], kind='bar', color=['seagreen', 'gold', 'firebrick'],
            width=0.8, ax=ax, position=1, stacked=True)
    # df.plot(x='session', y=['light_ave_period', 'medium_ave_period', 'severe_ave_period', 'total_ave_period'], kind='bar', color=['firebrick', 'gold', 'seagreen', 'navy'],
    #        ax=ax2, width=width, position=0, legend=False)
    ax.legend(['light', 'medium', 'severe'], loc=1)

    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=12)

    ax.set_xlabel('Session ID',fontsize=14)
    ax.set_ylabel('Total Count of Anomalies',fontsize=14)
    # ax2.set_ylabel('The average anomaly period (seconds)')
    # ax2.legend(loc=0)

    plt.show()
    plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.jpg")
    save_fig(fig, datafolder + "imgs//anomaly_cnt_per_session")

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    sorted_df.plot(x='session', y=['light_ave_period', 'medium_ave_period', 'severe_ave_period', 'total_ave_period'], kind='bar', color=['seagreen', 'gold', 'firebrick', 'navy'],
            width=1,ax=ax2, position=1)
    ax2.legend(['light', 'medium', 'severe', 'total'], loc=1)
    ax2.set_xlabel('Session ID',fontsize=14)
    ax2.set_ylabel('The average anomaly period (seconds)',fontsize=14)

    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=12)

    plt.show()
    plt.savefig(datafolder + "imgs//anomaly_ave_period_per_session.jpg")
    save_fig(fig2, datafolder + "imgs//anomaly_ave_period_per_session")

#####################################################################################
## @descr: Get the anomaly stats within each anomaly origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that counts the statistics of anomalies
## over each origin type
#####################################################################################
#def get_anomalies_stats_per_origin(datafolder, anomalies):
#    networks = loadJson(datafolder + "networks.json")



if __name__ == '__main__':
    datafolder = "D://Data//QRank//20170510//"
    anomaly_file = "merged_anomalies.json"

    anomalies = loadJson(datafolder+anomaly_file)
    # plot_anomalies_per_session(datafolder, anomalies)