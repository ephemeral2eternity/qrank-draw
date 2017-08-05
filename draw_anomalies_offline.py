import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from fig_utils import *
from analyze_anomalies_offline import *


#####################################################################################
## @descr: Plot the anomaly stats of each anomalous session in bar graph
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
## @return: pdf figures saved in datafolder/imgs
#####################################################################################
def plot_anomalies_per_session(session_anomalies, sorted_by="total_count", imgName="topN_sessions", top_n=10, drawTopN=True):
    anomalies_per_session = get_anomalies_stats_per_session(session_anomalies)
    # anomalies_per_session = loadJson(datafolder + "anomalies_per_session_cnt.json")

    df = pd.DataFrame(anomalies_per_session)
    sorted_df = df.sort_values(by=sorted_by, ascending=False)
    top_n_sorted_df = sorted_df.head(top_n)
    top_n_anomalies_num = sum(top_n_sorted_df['total_count'].values.tolist())
    all_anomalies_num = sum(df['total_count'].values.tolist())
    print("The top %d users account for %d QoE anomalies among all %d QoE anomalies!" % (top_n, top_n_anomalies_num, all_anomalies_num))

    if not drawTopN:
        top_n_sorted_df = df.sort_values(by=sorted_by, ascending=False)

    fig = plt.figure()
    ax = fig.add_subplot(311)


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
    ax.set_ylabel('#',fontsize=8)
    # ax2.set_ylabel('The average anomaly period (seconds)')
    # ax2.legend(loc=0)
    # ax.set_xticklabels(top_n_sorted_df['user'], rotation=60, ha="center")

    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.jpg")
    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.pdf")
    #plt.savefig(datafolder + "imgs//anomaly_cnt_per_session.png")
    #plt.show()


    # fig2 = plt.figure()
    ax2 = fig.add_subplot(312)
    top_n_sorted_df.plot(x='user', y=['light_ave_period', 'medium_ave_period', 'severe_ave_period', 'total_ave_period'], kind='bar', color=['seagreen', 'gold', 'firebrick', 'navy'],
            width=0.8,ax=ax2,sharex=ax, position=0.5, align='center')
    ax2.legend(['light', 'medium', 'severe', 'total'], loc='upper left', bbox_to_anchor=(0.85, 2.5))

    ax2.set_xlabel('Emulated Users',fontsize=10)
    ax2.set_ylabel('Avg DUR (sec)',fontsize=8)
    ax2.tick_params(axis='x', labelsize=8)
    ax2.set_xticklabels(top_n_sorted_df['user'], rotation=60, ha="right")

    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=10)

    imgName = imgfolder + imgName + "_by_" + sorted_by
    plt.savefig(imgName + ".jpg")
    plt.savefig(imgName + ".pdf")
    plt.savefig(imgName + ".png")
    plt.show()

    return anomalies_per_session

#####################################################################################
## @descr: Draw bar graphs over all origins
## @params: datafolder ----  the folder where the session QoE data are saved
##          anomalies ---- all anomaly data organized by session id
##          graph ---- "cloud_network", "transit_network", "access_network", "device", "server"
#####################################################################################
def draw_anomalies_stats_per_origin_type(session_anomalies, graph="access_network", img_name="all", top_n=3):
    data_to_draw = get_anomalies_stats_per_specific_origin_type(session_anomalies, graph)

    df = pd.DataFrame(data_to_draw)
    sorted_df = df.sort_values(by='total_count', ascending=False)

    top_n_sorted_df = sorted_df.head(top_n)
    top_n_anomalies_num = sum(top_n_sorted_df['total_count'].values.tolist())
    all_anomalies_num = sum(df['total_count'].values.tolist())
    print("The top %d %s account for %d QoE anomalies among all %d QoE anomalies!" % (
    top_n, graph, top_n_anomalies_num, all_anomalies_num))

    hs_dist = 0.1

    if "cloud" in graph:
        origin_name_label = "Cloud Network AS and Location"
        col_width = 0.4
        anno_font_size = 10
        x_offset = 0
        y_offset_cnt = 0.1
        y_offset_dur = 0.5
        hs_dist = 0.5
    elif ("transit" in graph) or ("access" in graph):
        origin_name_label = "Network AS and location"
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
    ax2.set_ylabel('Avg DUR (sec)',fontsize=10)
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

    if "access" in graph:
        bottom_dist = 0.5
    elif "transit" in graph:
        bottom_dist = 0.55
    elif "cloud" in graph:
        bottom_dist = 0.38
    else:
        bottom_dist = 0.5

    plt.subplots_adjust(hspace=hs_dist, bottom=bottom_dist)

    full_img_name = imgfolder + img_name + "_stats_" + graph

    fig.savefig(full_img_name + ".pdf")
    fig.savefig(full_img_name+ ".jpg")
    fig.savefig(full_img_name+ ".png")

    plt.show()


if __name__ == '__main__':
    ##################################################################################################################
    ## Section IV.B, get the anomalous system for QoE anomalies
    ## Table II
    pp = pprint.PrettyPrinter(indent=4)
    #anomalies_stats_per_origin_type = get_anomaly_stats_per_origin_type(session_anomalies)
    #pp.pprint(anomalies_stats_per_origin_type)

    ## Draw QoE anomaly statistics over different access networks as anomalous systems
    # anomalies_stats_per_access_networks = get_anomalies_stats_per_specific_origin_type(session_anomalies, "access_network")
    # pp.pprint((anomalies_stats_per_access_networks))
    '''
    session_anomalies = get_all_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(session_anomalies, graph="access_network", img_name="all")

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="access_network", img_name="persistent")

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="access_network", img_name="recurrent")

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="access_network", img_name="occasional")


    session_anomalies = get_all_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(session_anomalies, graph="transit_network", img_name="all")

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="transit_network", img_name="persistent")

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="transit_network", img_name="recurrent")

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="transit_network", img_name="occasional")
    '''

    session_anomalies = get_all_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(session_anomalies, graph="device", img_name="all")

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="device", img_name="persistent")

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="device", img_name="recurrent")

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="device", img_name="occasional")

