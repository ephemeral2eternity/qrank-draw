import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt_styles = ['k-', 'b-+', 'r-.', 'm--', 'y:', 'g-^', 'c-o', 'b--', 'r-<', 'm->']

## Draw QoE curves for different clients
def plot_qoe_curves(to_plot_qoes, start_ts, end_ts, img_name="qoes"):
    minTS = start_ts
    maxTS = end_ts

    fig, ax = plt.subplots()

    client_names = to_plot_qoes.keys()

    for client in client_names:
        qoes_dat = to_plot_qoes[client]
        ts = qoes_dat.keys()
        ts.sort()
        qoes = [qoes_dat[t] for t in ts]
        plt.plot(ts, qoes, plt_styles[client_names.index(client)], label=client)
        if minTS is None:
            minTS = min(ts)
        else:
            minTS = min(minTS, min(ts))

        if maxTS is None:
            maxTS = max(ts)
        else:
            maxTS = max(maxTS, max(ts))

    num_intvs = int((maxTS - minTS) / 600) + 1
    ts_labels = [minTS + x * 600 for x in range(num_intvs)]

    # str_ts = [datetime.datetime.fromtimestamp(x * 600 + minTS).strftime('%H:%M') for x in range(num_intvs)]
    str_ts = [datetime.datetime.utcfromtimestamp(x * 600).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=15)

    ax.set_xlabel("Time", fontsize=20)
    ax.set_ylabel("Chunk QoE (0 - 5)", fontsize=20)

    plt.ylim((0, 5.5))
    plt.xlim((minTS, maxTS))
    plt.legend()

    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")
    plt.show()