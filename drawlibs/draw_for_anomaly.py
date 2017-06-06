import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt_styles = ['k-', 'b-.', 'r--', 'm:', 'y-', 'g-.', 'c--']

styles = ['k-', 'b.-', 'r--', 'm:', 'ys-', 'go-', 'c^-',
          'k.-', 'b--', 'r:', 'ms-','yo-', 'g^-', 'c-',
          'k--', 'b:', 'rs-', 'mo-', 'y^-', 'g-', 'c.-',
          'k:', 'bs-', 'ro-', 'm^-', 'y-', 'g.-', 'c--']


def draw_networks_lats_for_anomaly(networks_lats, networks_info, startTS, endTS, anomalyStart, anomalyEnd, img_name, num_intvs=5):
    fig, ax = plt.subplots()
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
    ax.legend(h, l, loc = 'center left', bbox_to_anchor = (0.6, 0.8), ncol = 1)

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
    ax.legend(h1, l1, loc=0)

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
