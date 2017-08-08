import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from pylab import setp
import numpy as np
import pandas as pd

styles = ['k-', 'b.-', 'r--', 'm:', 'ys-', 'go-', 'c^-',
          'k.-', 'b--', 'r:', 'ms-','yo-', 'g^-', 'c-',
          'k--', 'b:', 'rs-', 'mo-', 'y^-', 'g-', 'c.-',
          'k:', 'bs-', 'ro-', 'm^-', 'y-', 'g.-', 'c--',
          'ks-', 'bo-', 'r^-', 'm-', 'y.-', 'g--', 'c-',
          'ko-', 'b^-', 'r-', 'm.-', 'y--', 'g-', 'cs-']


def draw_networks_lats_for_anomaly(networks_lats, networks_info, startTS, endTS, anomalyStart, anomalyEnd, img_name, num_intvs=5):
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    draw_id = 0
    for network_id in networks_lats.keys():
        if networks_lats[network_id]:
            cur_data = pd.DataFrame(networks_lats[network_id])
            sorted_data = cur_data.sort_values(by='timestamp', ascending=True)
            line_sty = styles[draw_id]
            curve_label = "AS " + str(networks_info[network_id]["as"]) + "@(" + str(networks_info[network_id]["latitude"]) + "," +  str(networks_info[network_id]["longitude"]) + ")"
            sorted_data.plot(x="timestamp", y="latency", ax=ax, label=curve_label, style=line_sty)
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
    ax.legend(h, l, bbox_to_anchor = (-0.05, -.5), loc = 'upper left', ncol = 2)

    plt.xlim((startTS, endTS))

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()

def draw_qoes_for_anomaly(qoes, startTS, endTS, anomaly_start, anomaly_end, img_name, num_intvs = 5):
    df = pd.DataFrame(qoes)
    sorted_df = df.sort_values(by='timestamp', ascending=True)
    tses = [float(qoe["timestamp"]) for qoe in qoes]

    fig, ax = plt.subplots()
    sorted_df.plot(x="timestamp", y="QoE", color='navy', ax=ax, label="QoE Curve")
    h1, l1 = ax.get_legend_handles_labels()

    ts_intvl = (endTS - startTS)/num_intvs
    ts_labels = [startTS + x * ts_intvl for x in range(num_intvs + 1)]
    str_ts = [datetime.datetime.fromtimestamp(x * ts_intvl + startTS).strftime('%H:%M:%S') for x in range(num_intvs + 1)]
    plt.xticks(ts_labels, str_ts, fontsize=12)

    ax.set_xlabel("Time", fontsize=16)
    ax.set_ylabel("Chunk QoE (0 - 5)", fontsize=16)

    ax.axvspan(anomaly_start, anomaly_end, facecolor='r', alpha=0.5)

    red_patch = mpatches.Patch(color='r', label="QoE Anomaly", alpha=0.5)
    h1.append(red_patch)
    l1.append("QoE Anomaly")
    ax.legend(h1, l1, loc=3)

    plt.ylim((0, 5.2))
    plt.xlim((startTS, endTS))

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()


def draw_session_lats_for_anomaly(session_lats, startTS, endTS, anomaly_start, anomaly_end, img_name, num_intvs = 5):
    df = pd.DataFrame(session_lats)
    sorted_df = df.sort_values(by='timestamp', ascending=True)

    fig, ax = plt.subplots()
    sorted_df.plot(x="timestamp", y="latency", color='navy', ax=ax, label="Latency curve")
    h1, l1 = ax.get_legend_handles_labels()

    ts_intvl = (endTS - startTS)/num_intvs
    ts_labels = [startTS + x * ts_intvl for x in range(num_intvs + 1)]
    str_ts = [datetime.datetime.fromtimestamp(x * ts_intvl + startTS).strftime('%H:%M:%S') for x in range(num_intvs + 1)]
    plt.xticks(ts_labels, str_ts, fontsize=12)

    ax.set_xlabel("Time", fontsize=16)
    ax.set_ylabel("Session latency (ms)", fontsize=16)

    ax.axvspan(anomaly_start, anomaly_end, facecolor='r', alpha=0.5)

    red_patch = mpatches.Patch(color='r', label="QoE Anomaly", alpha=0.5)
    h1.append(red_patch)
    l1.append("QoE Anomaly")
    ax.legend(h1, l1, loc=0)

    plt.ylim((df["latency"].min() - 2, df["latency"].max() + 2))
    plt.xlim((startTS, endTS))

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()


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
