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
## @descr: Get the anomalies within each anomaly origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################
def get_anomalies_per_origin_type(datafolder, anomalies):
    networks = loadJson(datafolder + "networks.json")
    sessions = loadJson(datafolder + "sessions.json")
    nodes = loadJson(datafolder + "nodes.json")
    anomalies_per_origin_type = {"cloud_network":[], "transit_network":[], "access_network":[], "total_network":[],
                                 "device":[], "path":[], "route_change":[], "server":[], "server_change":[]}
    for session_id in anomalies.keys():
        session_anomalies = anomalies[session_id]
        for anomaly in session_anomalies:
            duration = anomaly["end"] - anomaly["start"]
            for origin in anomaly["origins"]:
                if origin["type"] == "network":
                    origin_net = networks[str(origin["origin_mid"])]
                    if origin_net["type"] == "cloud":
                        anomalies_per_origin_type["cloud_network"].append({"count":origin["count"], "duration":duration,
                                                                           "network": str(origin_net["as"]) + "@(" +
                                                                                      str(origin_net["latitude"]) + "," +
                                                                                      str(origin_net["longitude"]) + ")",
                                                                           "isp":origin_net["name"], "as":origin_net["as"],
                                                                           "latitude":origin_net["latitude"], "longitude":origin_net["longitude"]})
                    elif origin_net["type"] == "transit":
                        anomalies_per_origin_type["transit_network"].append({"count": origin["count"], "duration": duration,
                                                                             "network": str(origin_net["as"]) + "@(" +
                                                                                      str(origin_net["latitude"]) + "," +
                                                                                      str(origin_net["longitude"]) + ")",
                                                                           "isp":origin_net["name"], "as":origin_net["as"],
                                                                           "latitude":origin_net["latitude"], "longitude":origin_net["longitude"]})
                    elif origin_net["type"] == "access":
                        anomalies_per_origin_type["access_network"].append({"count": origin["count"], "duration": duration,
                                                                            "network": str(origin_net["as"]) + "@(" +
                                                                                      str(origin_net["latitude"]) + "," +
                                                                                      str(origin_net["longitude"]) + ")",
                                                                           "isp":origin_net["name"], "as":origin_net["as"],
                                                                           "latitude":origin_net["latitude"], "longitude":origin_net["longitude"]})
                    anomalies_per_origin_type["total_network"].append({"count": origin["count"], "duration": duration,
                                                                       "network": str(origin_net["as"]) + "@(" +
                                                                                  str(origin_net["latitude"]) + "," +
                                                                                  str(origin_net["longitude"]) + ")",
                                                                       "isp":origin_net["name"], "as":origin_net["as"],
                                                                       "latitude":origin_net["latitude"], "longitude":origin_net["longitude"]})
                elif origin["type"] == "device":
                    session = sessions[session_id]
                    client_node = nodes[str(session["client"])]
                    anomalies_per_origin_type["device"].append({"count": origin["count"], "duration": duration, "client_ip":client_node["ip"]})
                elif origin["type"] == "path":
                    anomalies_per_origin_type["path"].append({"count": origin["count"], "duration": duration, "path": origin["data"]})
                elif origin["type"] == "route_change":
                    anomalies_per_origin_type["route_change"].append({"count": origin["count"], "duration": duration, "route_change":origin["data"]})
                elif origin["type"] == "server":
                    session = sessions[session_id]
                    server_node = nodes[str(session["server"])]
                    anomalies_per_origin_type["server"].append({"count": origin["count"], "duration": duration, "server_ip":server_node["ip"]})
                else:
                    anomalies_per_origin_type["server_change"].append({"count": origin["count"], "duration": duration, "server_change":origin["data"]})

    return anomalies_per_origin_type

#####################################################################################
## @descr: Get the total count and mean duration for a list of anomalies
## @params: anomalies ---- a list of anomalies, each has "count" and "duration" params.
## @return: anomaly_origin_type ---- Add up the total count and average duration
#####################################################################################
def get_stats_from_anomalies(anomalies):
    total_cnt = 0
    total_duration = 0
    for anomaly in anomalies:
        total_cnt += anomaly["count"]
        total_duration += anomaly["duration"]

    if len(anomalies) > 0:
        ave_duration = total_duration / float(len(anomalies))
    else:
        ave_duration = -1
    return total_cnt, ave_duration


#####################################################################################
## @descr: Get the anomalies within each anomaly origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################
def get_anomalies_stats_per_origin_type(datafolder, anomalies):
    anomalies_per_origin_type = get_anomalies_per_origin_type(datafolder, anomalies)
    anomalies_stats_per_origin_type = {}
    for origin_type in anomalies_per_origin_type.keys():
        total_cnt, ave_duration = get_stats_from_anomalies(anomalies_per_origin_type[origin_type])
        anomalies_stats_per_origin_type[origin_type] = {"total_count":total_cnt, "ave_duration":ave_duration}

    return anomalies_stats_per_origin_type

#####################################################################################
## @descr: Get the anomalies stats per origin type over all origins
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
##          graph ---- "cloud_network", "transit_network", "access_network", "device", "server"
## @return: data_to_draw ---- the data to draw
#####################################################################################
def get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, graph):
    anomalies_per_origin_type = get_anomalies_per_origin_type(datafolder, anomalies)
    anomalies_to_study = anomalies_per_origin_type[graph]

    anomalies_per_origins = {}
    if "cloud" in graph:
        origin_key_word = "network"
    elif "network" in graph:
        origin_key_word = "as"
    elif "device" in graph:
        origin_key_word = "client_ip"
    elif "server" in graph:
        origin_key_word = "server_ip"
    else:
        exit(-1)

    for anomaly in anomalies_to_study:
        if anomaly[origin_key_word] not in anomalies_per_origins.keys():
            anomalies_per_origins[anomaly[origin_key_word]] = []
        anomalies_per_origins[anomaly[origin_key_word]].append(anomaly)

    data_to_draw = []
    for origin in anomalies_per_origins.keys():
        cur_origin_anomalies = anomalies_per_origins[origin]
        cur_origin_total_cnt, cur_origin_ave_duration = get_stats_from_anomalies(cur_origin_anomalies)
        data_to_draw.append({"total_count": cur_origin_total_cnt, "ave_duration": cur_origin_ave_duration, origin_key_word: origin})

    print(json.dumps(data_to_draw, indent=4))

    return data_to_draw


#####################################################################################
## @descr: Draw bar graphs over all origins
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
##          graph ---- "cloud_network", "transit_network", "access_network", "device", "server"
#####################################################################################
def draw_anomalies_stats_per_origin_type(datafolder, anomalies, graph="access_network"):
    # data_to_draw = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, graph)
    data_to_draw = loadJson(datafolder + "/todraw/descr/anomaly_stats_" + graph + "_revised.json")
    df = pd.DataFrame(data_to_draw)
    sorted_df = df.sort_values(by='total_count', ascending=False)

    if "cloud" in graph:
        origin_key_word = "location"
    elif "network" in graph:
        origin_key_word = "ASName"
    elif "device" in graph:
        origin_key_word = "client_name"
    elif "server" in graph:
        origin_key_word = "server_ip"
    else:
        exit(-1)

    fig = plt.figure(1)
    ax = fig.add_subplot(211)

    sorted_df.plot(x=origin_key_word, y='total_count', kind='bar', color='navy',
            width=1, ax=ax, position=1)

    # ax.set_xlabel('Network',fontsize=10)
    ax.set_ylabel('Total Count \n of anomalies (#)',fontsize=12)
    plt.yticks(fontsize=8)
    ax.legend().set_visible(False)
    plt.ylim((0, 120))

    x_offset = -0.5
    y_offset = 0.2
    for p in ax.patches:
        b = p.get_bbox()
        val = "{:.1f}".format(b.y1 + b.y0)
        ax.annotate(val, ((b.x0 + b.x1) / 2 + x_offset, b.y1 + y_offset), fontsize=8)

    ax2 = fig.add_subplot(212)
    sorted_df.plot(x=origin_key_word, y='ave_duration', kind='bar', color='navy',
            width=1,ax=ax2, sharex=ax)
    # ax2.legend(['light', 'medium', 'severe', 'total'], loc=1)
    # ax2.set_xlabel('Locations for AS 15133\nMCI Communications Services, Inc. d/b/a Verizon Business',fontsize=12)
    ax2.set_xlabel('AS Names', fontsize=12)
    ax2.set_ylabel('The average duration\n of anomalies (seconds)',fontsize=12)
    # ax.legend(['AS 15133'], fontsize=10)
    # ax2.legend(['MCI Communications Services, Inc. d/b/a Verizon Business'])
    ax2.legend().set_visible(False)

    x_offset = -0.5
    y_offset = 20
    for p in ax2.patches:
        b = p.get_bbox()
        val = "{:.1f}".format(b.y1 + b.y0)
        ax2.annotate(val, ((b.x0 + b.x1) / 2 + x_offset, b.y1 + y_offset), fontsize=8)

    plt.ylim((0, 8000))
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.subplots_adjust(hspace=0.05, bottom=0.35)
    plt.show()

    fig.savefig(datafolder + "imgs/anomaly_stat_" + graph + ".pdf")
    fig.savefig(datafolder + "imgs/anomaly_stat_" + graph + ".jpg")

#####################################################################################
## @descr: plot the anomalies over a certain types of origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################

if __name__ == '__main__':
    # datafolder = "/Users/chenw/Data/QRank/20170510/"
    datafolder = "D://Data/QRank/20170510/"
    anomaly_file = "merged_anomalies.json"

    anomalies = loadJson(datafolder+anomaly_file)
    # plot_anomalies_per_session(datafolder, anomalies)
    # anomalies_per_origin_type = get_anomalies_per_origin_type(datafolder, anomalies)
    # print(json.dumps(anomalies_per_origin_type, indent=4))
    # anomaly_stats_per_origin_type = get_anomalies_stats_per_origin_type(datafolder, anomalies)
    # print(json.dumps(anomaly_stats_per_origin_type, indent=4))

    #anomalies_stats_for_cloud_net = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "cloud_network")
    #dumpJson(anomalies_stats_for_cloud_net, datafolder + "rsts/anomaly_stats_cloud_network.json")

    #anomalies_stats_for_access_net = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "access_network")
    #dumpJson(anomalies_stats_for_access_net, datafolder + "rsts/anomaly_stats_access_network.json")

    #anomalies_stats_for_transit_net = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "transit_network")
    #dumpJson(anomalies_stats_for_transit_net, datafolder + "rsts/anomaly_stats_transit_network.json")

    # print(json.dumps(anomalies_stats_per_specific_origin, indent=4))
    draw_anomalies_stats_per_origin_type(datafolder, anomalies, "device")

    #data_to_draw = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "device")
    #dumpJson(data_to_draw, datafolder + "todraw/descr/anomaly_stats_device.json")