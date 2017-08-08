import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from json_utils import *
import pprint
from fig_utils import *
from drawlibs.plot_qoe_curves import *
from drawlibs.draw_for_anomaly import *
import numpy as np
from get_objects import *
import glob

#####################################################################################
## @descr: Plot the latencies probed by traceroute for all links in a session
##         within an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_link_lats_for_anomaly(session_id, anomaly_ts, cushion=600):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_ts)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - cushion
    draw_end = anomaly_end + cushion

    link_objs = session["links"]
    link_ids = link_objs.keys()

    link_details = get_link_details(link_objs)
    link_lats = get_link_lats_in_range(link_ids, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(int(anomaly_ts)) + "_session_" + str(session_id) + "_link_lats"
    draw_links_lats_for_anomaly(link_lats, link_details, draw_start, draw_end, anomaly_start, anomaly_end, img_name)


#####################################################################################
## @descr: Draw the link latencies within an anomalous period
## @params: link_lats --- latencies for all links to be drawn, the key is the link id.
##          link_details --- the details of each link, including the src and dst node ips and
##                           the src and dst node networks' names.
##          draw_start --- the start time stamp of all link latencies to be drawn
##          draw_end ---- the end time stamp of all link latencies to be drawn
##          anomaly_start ---- the anomaly period start timestamp to label
##          anomaly_end ---- the anomaly period end timestamp to label
##          img_name ---- the file name to save the iamge
#####################################################################################
def draw_links_lats_for_anomaly(link_lats, link_details, startTS, endTS, anomalyStart, anomalyEnd, img_name, num_intvs=5):
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 2)
    draw_id = 0
    for link_id in link_lats.keys():
        if link_lats[link_id]:
            cur_data = pd.DataFrame(link_lats[link_id])
            sorted_data = cur_data.sort_values(by='timestamp', ascending=True)
            line_sty = styles[draw_id]
            curve_label = link_details[link_id]["src"] + "(AS " + str(link_details[link_id]["srcNet"]) + ")" + "<--->" + link_details[link_id]["dst"] + "(AS " + str(link_details[link_id]["dstNet"]) + ")"
            sorted_data.plot(x="timestamp", y="latency", ax=ax, label=curve_label, style=line_sty)
            anomaly_period_data = cur_data[cur_data["timestamp"].between(anomalyStart, anomalyEnd, inclusive=True)]
            anomaly_period_mean = anomaly_period_data["latency"].mean()
            anomaly_period_std = anomaly_period_data["latency"].std()
            print("%s Mean: %.4f ;Std: %.4f"%(curve_label, anomaly_period_mean, anomaly_period_std))
            draw_id += 1

    h, l = ax.get_legend_handles_labels()

    ts_intvl = (endTS - startTS)/num_intvs
    ts_labels = [startTS + x * ts_intvl for x in range(num_intvs + 1)]
    str_ts = [datetime.datetime.fromtimestamp(x * ts_intvl + startTS).strftime('%H:%M:%S') for x in range(num_intvs + 1)]
    plt.xticks(ts_labels, str_ts, fontsize=12)

    ax.set_xlabel("Time", fontsize=16)
    ax.set_ylabel("Latency (ms)", fontsize=16)

    ax.axvspan(anomalyStart, anomalyEnd, facecolor='r', alpha=0.5)

    red_patch = mpatches.Patch(color='r', label="QoE Anomaly", alpha=0.5)
    h.append(red_patch)
    l.append("QoE Anomaly")
    params = {'legend.fontsize': 10}
    plt.rcParams.update(params)

    ax.legend(h, l, bbox_to_anchor=(0, 1.01), loc="lower left", ncol=1, mode="expand")

    plt.xlim((startTS, endTS))

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()

#####################################################################################
## @descr: Plot the probed latencies from the client node to all routers in the session
## @params: anomaly_ts --- the anomaly that spread across the timestamp
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMean", cushion=600):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_ts)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - cushion
    draw_end = anomaly_end + cushion

    probed_lats = get_probed_lats_in_range(session_id, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(int(anomaly_ts)) + "_session_" + str(session_id) + "_" + rttToDraw
    draw_probed_lats_for_anomaly(probed_lats, draw_start, draw_end, anomaly_start, anomaly_end, img_name, rttToDraw, num_intvs=5)

#####################################################################################
## @descr: Draw the probed router latencies within an anomalous period
## @params: probed_lats --- latencies probed from the user to all routers in its route
##          draw_start --- the start time stamp of all link latencies to be drawn
##          draw_end ---- the end time stamp of all link latencies to be drawn
##          anomaly_start ---- the anomaly period start timestamp to label
##          anomaly_end ---- the anomaly period end timestamp to label
##          img_name ---- the file name to save the iamge
#####################################################################################
def draw_probed_lats_for_anomaly(probed_lats, startTS, endTS, anomalyStart, anomalyEnd, img_name, rttToDraw="rttMean", num_intvs=5):
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 2)
    draw_id = 0
    for router in probed_lats.keys():
        node_as = get_node_as_by_ip(router)
        if probed_lats[router]:
            cur_data = pd.DataFrame(probed_lats[router])
            anomaly_period_data = cur_data[cur_data["TS"].between(anomalyStart, anomalyEnd, inclusive=True)]
            anomaly_period_mean = anomaly_period_data[rttToDraw].mean()

            sorted_data = cur_data.sort_values(by='TS', ascending=True)
            line_sty = styles[draw_id]
            curve_label = router + "(AS " + str(node_as) + ")"
            sorted_data.plot(x="TS", y=rttToDraw, ax=ax, label=curve_label, style=line_sty)
            print("The %s data on curve %s during anomaly period has average of %.4f." % (rttToDraw, curve_label, anomaly_period_mean))
            draw_id += 1

    h, l = ax.get_legend_handles_labels()

    ts_intvl = (endTS - startTS)/num_intvs
    ts_labels = [startTS + x * ts_intvl for x in range(num_intvs + 1)]
    str_ts = [datetime.datetime.fromtimestamp(x * ts_intvl + startTS).strftime('%H:%M:%S') for x in range(num_intvs + 1)]
    plt.xticks(ts_labels, str_ts, fontsize=12)

    ax.set_xlabel("Time", fontsize=16)
    if rttToDraw == "rttMin":
        ax.set_ylabel("Min Latency (ms)", fontsize=16)
    elif rttToDraw == "rttMax":
        ax.set_ylabel("Max Latency (ms)", fontsize=16)
    elif rttToDraw == "rttLoss":
        ax.set_ylabel("Packet loss rate (100%)", fontsize=16)
    else:
        ax.set_ylabel("Mean Latency (ms)", fontsize=16)

    ax.axvspan(anomalyStart, anomalyEnd, facecolor='r', alpha=0.5)

    red_patch = mpatches.Patch(color='r', label="QoE Anomaly", alpha=0.5)
    h.append(red_patch)
    l.append("QoE Anomaly")
    params = {'legend.fontsize': 10}
    plt.rcParams.update(params)

    ax.legend(h, l, bbox_to_anchor=(0.1, 1.01), loc="lower center", ncol=1, mode="expand")

    plt.xlim((startTS, endTS))

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()


#####################################################################################
## @descr: Merged all probed latency raw csv files to one json file and dump it to probedfolder
#####################################################################################
def merge_all_network_lats():
    sessions = loadJson(datafolder+session_file)
    for session_id, session_obj in sessions.iteritems():
        client_id = session_obj["client"]
        client_obj = get_node(client_id)
        client_name = client_obj["name"]
        print("Merging probed latencies for session %s with user name %s" % (session_id, client_name))
        client_folder = raw_monitor_folder + client_name + "/"
        rtt_files = glob.glob(client_folder + "*_RTT.csv")
        rtts = []
        for rtt_file in rtt_files:
            cur_rtt = csv2json(rtt_file)
            rtts.extend(cur_rtt)
        if len(rtts) > 0:
            df = pd.DataFrame(rtts)
            df[['TS', 'rttLoss', 'rttMax', 'rttMean', 'rttMin', 'rttStd']] = df[['TS', 'rttLoss', 'rttMax', 'rttMean', 'rttMin', 'rttStd']].apply(pd.to_numeric, errors='coerce')
            sorted_df = df.sort_values(by='TS', ascending=True)
            sorted_json_str = sorted_df.to_json(orient='records')
            sorted_json = json.loads(sorted_json_str)
            dumpJson(sorted_json, probed_folder + "session_" + str(session_id) + "_lats.json")

#####################################################################################
## @descr: Plot the qoes values within an anomaly period
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the anomalous period
#####################################################################################
def plot_qoes_for_anomaly(session_id, anomaly_ts):
    anomaly = get_anomaly(session_id, anomaly_ts)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    # pp.pprint(anomaly)
    anomaly_duration = anomaly_end - anomaly_start
    print("The anomaly to be drawn lasts %.2f seconds" % anomaly_duration)

    draw_start = anomaly_start - period
    draw_end = anomaly_end + period
    session_id = anomaly["session_id"]

    session_qoes = get_session_qoes_in_range(session_id, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(int(anomaly_ts)) + "_session_" + str(session_id) + "_qoes"

    ## Revise it to draw multiple session qoes to reflect the QoEs on related sessions.
    draw_qoes_for_anomaly(session_qoes, draw_start, draw_end, anomaly_start, anomaly_end, img_name, num_intvs=5)


if __name__ == '__main__':
    ## Merge all raw probed latency files into a json file per session
    # merge_all_network_lats()


    ## Section V.B 1), Figure 11
    # session_id = 37
    # anomaly_ts = 1499760630

    ## Section V.B 2), Figure 12
    session_id = 9
    anomaly_ts = 1499780567
    # anomaly_ts = 1499791958
    plot_qoes_for_anomaly(session_id, anomaly_ts)

    plot_link_lats_for_anomaly(session_id, anomaly_ts)

    ## Section V.A 1), Figure 8 (c)
    #pp = pprint.PrettyPrinter(indent=4)

    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMean")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMin")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMax")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttStd")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttLoss")