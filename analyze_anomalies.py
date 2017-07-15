from json_utils import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from fig_utils import *
from data_folder import *
from get_objects import *
from get_asname import *
from get_address import *

#####################################################################################
## @descr: Classify the anomalies according to their top origin types
## @params: anomalies_cnt_per_session ---- all anomaly statistics per session
## @return: the session # for the type of anomalous sessions: occasional/recurrent/persistent
#####################################################################################
def classify_anomalous_sessions(anomalies_cnt_per_session):
    session_types = {"occasional":[], "recurrent":[], "persistent":[], "others":[]}
    for session_dict in anomalies_cnt_per_session:
        session_details = get_session(session_dict["session"])
        session_user = get_node(session_details["client"])["name"]
        if (session_dict["total_count"] < 50) and (session_dict["total_ave_period"] < 60):
            session_types["occasional"].append({session_dict["session"]:session_user})
        elif (session_dict["total_count"] >= 50) and (session_dict["total_ave_period"] < 60):
            session_types["recurrent"].append({session_dict["session"]:session_user})
        elif session_dict["total_ave_period"] >= 60:
            session_types["persistent"].append({session_dict["session"]:session_user})
        else:
            session_types["others"].append({session_dict["session"]:session_user})

    print(session_types)
    return session_types

#####################################################################################
## @descr: Get some statistics about all anomalies
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly  data
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def statsAnomaliesPerType(anomalies):
    session_cnts_per_type = {"light":0, "medium":0, "severe":0, "total":len(anomalies.keys())}
    anomaly_cnts_per_type = {"light":0, "medium":0, "severe":0, "total":0}
    anomaly_ave_duration_per_type = {"light":0, "medium":0, "severe":0, "total":0}

    for session_id, session_anomalies in anomalies.iteritems():
        session_anomaly_types = []
        # print("Study session %s!" % session_id)
        for anomaly in session_anomalies:
            # print("Study anomaly %s!" % anomaly["id"])
            anomaly_type = anomaly["type"]
            if anomaly_type not in session_anomaly_types:
                session_anomaly_types.append(anomaly_type)
            anomaly_cnts_per_type[anomaly_type] += 1
            anomaly_cnts_per_type["total"] += 1
            anomaly_period = float(anomaly["end"]) - float(anomaly["start"])
            anomaly_ave_duration_per_type[anomaly_type] += anomaly_period
            anomaly_ave_duration_per_type["total"] += anomaly_period

        if "severe" in session_anomaly_types:
            session_cnts_per_type["severe"] += 1
        if "medium" in session_anomaly_types:
            session_cnts_per_type["medium"] += 1
        if "light" in session_anomaly_types:
            session_cnts_per_type["light"] += 1

    for ano_type in anomaly_cnts_per_type.keys():
        if anomaly_cnts_per_type[ano_type] > 0:
            anomaly_ave_duration_per_type[ano_type] = anomaly_ave_duration_per_type[ano_type] / float(anomaly_cnts_per_type[ano_type])
        else:
            anomaly_ave_duration_per_type[ano_type] = -1

    anomaly_stats = {"session": session_cnts_per_type, "anomalies":anomaly_cnts_per_type, "duration":anomaly_ave_duration_per_type}
    return anomaly_stats

#####################################################################################
## @descr: Get the anomaly statistics per session
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: the statistics about the type of anomalous sessions, the type of anomalies
## the average duration of all types of anomalies
#####################################################################################
def get_anomalies_stats_per_session(anomalies):
    anomalies_per_session = []
    for session_id, session_anomalies in anomalies.iteritems():
        session = get_session(session_id)
        client_id = session["client"]
        user_node = get_node(client_id)
        session_dict = {"session":session_id, "user":user_node["name"]}
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
## @descr: Plot the anomaly stats of each anomalous session in bar graph
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: pdf figures saved in datafolder/imgs
#####################################################################################
def plot_anomalies_per_session(anomalies):
    anomalies_per_session = get_anomalies_stats_per_session(anomalies)
    dumpJson(anomalies_per_session, datafolder + "anomalies_per_session_cnt.json")
    # anomalies_per_session = loadJson(datafolder + "anomalies_per_session_cnt.json")

    df = pd.DataFrame(anomalies_per_session)
    sorted_df = df.sort_values(by='total_count', ascending=False)
    top_n_sorted_df = sorted_df.head(top_n)
    top_n_anomalies_num = sum(top_n_sorted_df['total_count'].values.tolist())
    all_anomalies_num = sum(df['total_count'].values.tolist())
    print("The top %d users account for %d QoE anomalies among all %d QoE anomalies!" % (top_n, top_n_anomalies_num, all_anomalies_num))

    fig = plt.figure()
    ax = fig.add_subplot(511)


    top_n_sorted_df.plot(x='user', y=['light_count', 'medium_count', 'severe_count'], kind='bar', color=['seagreen', 'gold', 'firebrick'],
            width=0.8, ax=ax, position=0.5, stacked=True, legend=False)
    # df.plot(x='session', y=['light_ave_period', 'medium_ave_period', 'severe_ave_period', 'total_ave_period'], kind='bar', color=['firebrick', 'gold', 'seagreen', 'navy'],
    #        ax=ax2, width=width, position=0, legend=False)
    # ax.legend(['light', 'medium', 'severe'], loc=1)
    # ax.legend.set_visible(False)

    #leg = plt.gca().get_legend()
    #ltext = leg.get_texts()
    #plt.setp(ltext, fontsize=14)

    # ax.tick_params(axis='x', labelsize=14, length=6, width=2)
    # ax.set_xlabel('Emulated Users',fontsize=14)
    ax.set_ylabel('Count',fontsize=12)
    # ax2.set_ylabel('The average anomaly period (seconds)')
    # ax2.legend(loc=0)
    # ax.set_xticklabels(top_n_sorted_df['user'], rotation=60, ha="center")

    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.jpg")
    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.pdf")
    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.png")
    #plt.show()


    # fig2 = plt.figure()
    ax2 = fig.add_subplot(512)
    top_n_sorted_df.plot(x='user', y=['light_ave_period', 'medium_ave_period', 'severe_ave_period', 'total_ave_period'], kind='bar', color=['seagreen', 'gold', 'firebrick', 'navy'],
            width=0.8,ax=ax2,sharex=ax, position=0.5, align='center')
    ax2.legend(['light', 'medium', 'severe', 'total'], loc='upper left', bbox_to_anchor=(0.85, 2.5))

    ax2.set_xlabel('Emulated Users',fontsize=14)
    ax2.set_ylabel('Avg duration \n (sec)',fontsize=12)
    ax2.tick_params(axis='x', labelsize=12)
    ax2.set_xticklabels(top_n_sorted_df['user'], rotation=75, ha="right")

    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=12)

    plt.savefig(datafolder + "imgs//anomaly_stat_per_session.jpg")
    plt.savefig(datafolder + "imgs//anomaly_stat_per_session.pdf")
    plt.savefig(datafolder + "imgs//anomaly_stat_per_session.png")
    plt.show()

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
    anomalies_per_origin_type = {"network": [], "cloud":[], "transit":[], "access":[],
                                 "device":[], "path":[], "route_change":[], "server":[], "server_change":[]}
    for session_id in anomalies.keys():
        session_anomalies = anomalies[session_id]
        for anomaly in session_anomalies:
            origin_exists = {"network": False, "cloud":False, "transit":False, "access":False,
                                 "device":False, "path":False, "route_change":False, "server":False, "server_change":False}
            for origin in anomaly["origins"]:
                if origin["type"] == "network":
                    origin_exists["network"] = True
                    origin_net = networks[str(origin["origin_mid"])]
                    origin_exists[origin_net["type"]] = True
                else:
                    origin_exists[origin["type"]] = True

            for origin_type in origin_exists.keys():
                if origin_exists[origin_type]:
                    anomalies_per_origin_type[origin_type].append(anomaly)

    return anomalies_per_origin_type

#####################################################################################
## @descr: Get the total count and mean duration for a list of anomalies
## @params: anomalies ---- a list of anomalies, each has "count" and "duration" params.
## @return: anomaly_origin_type ---- Add up the total count and average duration
#####################################################################################
def get_stats_from_anomalies(anomalies):
    total_cnt = len(anomalies)
    total_duration = 0
    for anomaly in anomalies:
        total_duration += float(anomaly["end"]) - float(anomaly["start"])

    if total_cnt > 0:
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
def get_anomalies_stats_per_specific_origin_type(anomalies, origin_typ):
    anomalies_per_origin_type = get_anomalies_per_origin_type(datafolder, anomalies)
    anomalies_to_study = anomalies_per_origin_type[origin_typ]

    anomalies_per_origins = {}
    networks_to_save = []
    for anomaly in anomalies_to_study:
        for origin in anomaly["origins"]:
            ## Get origin_name and cur_origin_type for current anomaly origin
            if (origin["type"] == "network"):
                origin_net = get_network(origin["origin_mid"])
                cur_origin_type = origin_net["type"]
                if cur_origin_type == "cloud":
                    addr = get_address_by_coords(origin_net["latitude"], origin_net["longitude"])
                    origin_name = get_asname(origin_net["as"]) + "\n" + addr
                else:
                    origin_name = get_asname(origin_net["as"])

                del origin_net["nodes"]
                del origin_net["related_sessions"]
                networks_to_save.append(origin_net)
            elif origin["type"] in ["server", "device"]:
                cur_origin_type = origin["type"]
                session = get_session(anomaly["session_id"])
                if cur_origin_type == "server":
                    origin_node_id = session["server"]
                else:
                    origin_node_id = session["client"]
                origin_node = get_node(origin_node_id)
                origin_name = origin_node["name"]
            else:
                cur_origin_type = origin["type"]
                origin_name = origin["data"]

            ## If current anomaly origin is the type of origin to study, append the anomaly under the origin name
            if cur_origin_type == origin_typ:
                if origin_name not in anomalies_per_origins.keys():
                    anomalies_per_origins[origin_name] = []
                anomalies_per_origins[origin_name].append(anomaly)

    dumpJson(networks_to_save, rstsfolder + "anomalous-" + origin_typ + "-networks-list.json")

    anomalies_stats_per_origins = []
    for origin in anomalies_per_origins.keys():
        cur_origin_anomalies = anomalies_per_origins[origin]
        cur_origin_total_cnt, cur_origin_ave_duration = get_stats_from_anomalies(cur_origin_anomalies)
        anomalies_stats_per_origins.append({"total_count": cur_origin_total_cnt, "ave_duration": cur_origin_ave_duration, "origin_name": origin})

    return anomalies_stats_per_origins


#####################################################################################
## @descr: Draw bar graphs over all origins
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
##          graph ---- "cloud_network", "transit_network", "access_network", "device", "server"
#####################################################################################
def draw_anomalies_stats_per_origin_type(anomalies, graph="access"):
    data_to_draw = get_anomalies_stats_per_specific_origin_type(anomalies, graph)
    df = pd.DataFrame(data_to_draw)
    sorted_df = df.sort_values(by='total_count', ascending=False)
    hs_dist = 0.1

    if graph == "cloud":
        origin_name_label = "Cloud Network Location"
        col_width = 0.4
        anno_font_size = 10
        x_offset = 0
        y_offset_cnt = 0.1
        y_offset_dur = 0.5
        hs_dist = 0.5
    elif graph in ["transit", "access"]:
        origin_name_label = "Network AS Name"
        col_width = 1.0
        anno_font_size = 6
        x_offset = -0.5
        y_offset_cnt = 0.2
        y_offset_dur = 20
    elif graph == "device":
        origin_name_label = "Emulated User"
        col_width = 0.8
        anno_font_size = 6
        x_offset = 0
        y_offset_cnt = 0.5
        y_offset_dur = 2
    elif "server" in graph:
        origin_name_label = "Server IP"
        col_width = 0.8
        anno_font_size = 8
        x_offset = 0
        y_offset_cnt = 0.5
        y_offset_dur = 2
    else:
        origin_name_label = "Event details"
        col_width = 0.8
        anno_font_size = 8
        x_offset = 0
        y_offset_cnt = 0.5
        y_offset_dur = 2

    fig = plt.figure(1)
    ax = fig.add_subplot(211)

    sorted_df.plot(x='origin_name', y='total_count', kind='bar', color='navy',
            width=col_width, ax=ax, position=1)

    # ax.set_xlabel(origin_name_label, fontsize=12)
    ax.set_ylabel('Count',fontsize=10)
    plt.yticks(fontsize=9)
    ax.legend().set_visible(False)
    # plt.ylim((0, 120))


    for p in ax.patches:
        b = p.get_bbox()
        val = "{:.0f}".format(b.y1 + b.y0)
        ax.annotate(val, ((b.x0 + b.x1) / 2 + x_offset, b.y1 + y_offset_cnt), fontsize=anno_font_size, color='blue')

    ax2 = fig.add_subplot(212)
    sorted_df.plot(x='origin_name', y='ave_duration', kind='bar', color='navy',
            width=col_width,ax=ax2, sharex=ax)
    # ax2.legend(['light', 'medium', 'severe', 'total'], loc=1)
    # ax2.set_xlabel('Locations for AS 15133\nMCI Communications Services, Inc. d/b/a Verizon Business',fontsize=12)
    ax2.set_xlabel(origin_name_label, fontsize=12)
    ax2.set_ylabel('The avg \nduration (sec)',fontsize=10)
    # ax.legend(['AS 15133'], fontsize=10)
    # ax2.legend(['MCI Communications Services, Inc. d/b/a Verizon Business'])
    ax2.legend().set_visible(False)

    for p in ax2.patches:
        b = p.get_bbox()
        val = "{:.1f}".format(b.y1 + b.y0)
        ax2.annotate(val, ((b.x0 + b.x1) / 2 + x_offset, b.y1 + y_offset_dur), fontsize=anno_font_size, color='blue')

    # plt.ylim((0, 8000))
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)

    if graph == "access":
        bottom_dist = 0.5
    elif graph == "transit":
        bottom_dist = 0.55
    elif graph == "cloud":
        bottom_dist = 0.38
    else:
        bottom_dist = 0.4

    plt.subplots_adjust(hspace=hs_dist, bottom=bottom_dist)

    fig.savefig(datafolder + "imgs/anomaly_stats_" + graph + ".pdf")
    fig.savefig(datafolder + "imgs/anomaly_stats_" + graph + ".jpg")
    fig.savefig(datafolder + "imgs/anomaly_stats_" + graph + ".png")

    plt.show()

#####################################################################################
## @descr: plot the anomalies over a certain types of origin type
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: anomaly_origin_type ---- the dictionary that contains the count and duration of all anomalies
## that locates the anomalies over the origin type
#####################################################################################

if __name__ == '__main__':
    # datafolder = "/Users/chenw/Data/QRank/20170510/"
    datafolder = "D://Data/QRank/20170712/"
    # anomaly_file = "merged_anomalies_revised.json"      ## revised file remove the dallas client that is bad all the time
    anomaly_file = "merged_anomalies.json"
    ## Read anomalies after merging
    anomalies = loadJson(datafolder + anomaly_file)

    #####################################################################################################
    ## Get the # and mean duration of anomalies and anomalous users per each type: severe, medium, light
    ## Table: : Statistics of QoE anomalies detected by QRank
    anomaly_stats = statsAnomaliesPerType(anomalies)
    print(anomaly_stats)

    #####################################################################################################
    ## Get the # and the average duration of QoE anomalies per user
    # Section 6.3: QoE anomalies per user
    plot_anomalies_per_session(anomalies)

    #####################################################################################################
    ## Get the anomalous session types
    # Table: # of users with QoE anomalies
    anomalies_per_session = get_anomalies_stats_per_session(anomalies)
    anomalous_session_types = classify_anomalous_sessions(anomalies_per_session)
    dumpJson(anomalous_session_types, rstsfolder + "anomalous_session_types.json")
    print("######################### Anomalous Session Types ########################")
    print("Total number of users: " + str(count_total_sessions()))
    print("Total number of users with QoE anomalies: " + str(len(anomalies_per_session)))
    print("Total number of users with occasional QoE anomalies: " + str(len(anomalous_session_types["occasional"])))
    print("Total number of users with recurrent QoE anomalies: " + str(len(anomalous_session_types["recurrent"])))
    print("Total number of users with persistent QoE anomalies: " + str(len(anomalous_session_types["persistent"])))
    print("##########################################################################")

    #####################################################################################################
    ## Get the # and average duration of QoE anomalies per origin type
    # Table: Table Y:  QoE anomaly statistics per origin types
    anomalies_per_origin_type = get_anomalies_per_origin_type(datafolder, anomalies)
    dumpJson(anomalies_per_origin_type, rstsfolder + "anomalies_per_origin_type.json")
    anomaly_stats_per_origin_type = get_anomalies_stats_per_origin_type(datafolder, anomalies)
    dumpJson(anomaly_stats_per_origin_type, rstsfolder + "anomaly_stats_per_origin_type.json")

    anomalies_stats_for_cloud_net = get_anomalies_stats_per_specific_origin_type(anomalies, "cloud")
    dumpJson(anomalies_stats_for_cloud_net, datafolder + "rsts/anomaly_stats_cloud_network.json")
    draw_anomalies_stats_per_origin_type(anomalies, "transit")
    draw_anomalies_stats_per_origin_type(anomalies, "access")
    draw_anomalies_stats_per_origin_type(anomalies, "cloud")

    #anomalies_stats_for_access_net = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "access_network")
    #dumpJson(anomalies_stats_for_access_net, datafolder + "rsts/anomaly_stats_access_network.json")

    #anomalies_stats_for_transit_net = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "transit_network")
    #dumpJson(anomalies_stats_for_transit_net, datafolder + "rsts/anomaly_stats_transit_network.json")

    # print(json.dumps(anomalies_stats_per_specific_origin, indent=4))
    # draw_anomalies_stats_per_origin_type(datafolder, anomalies, "device")

    #data_to_draw = get_anomalies_stats_per_specific_origin_type(datafolder, anomalies, "device")
    #dumpJson(data_to_draw, datafolder + "todraw/descr/anomaly_stats_device.json")