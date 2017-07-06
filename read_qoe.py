import csv

from drawlibs.plot_qoe_curves import *
from get_file import *


def read_qoe(filename, ts_start, ts_end):
    qoes = {}
    print filename
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        chunk_no = 0
        for qoe_obj in reader:
            ts = float(qoe_obj["TS"])
            if (ts > ts_start) and (ts < ts_end) and (chunk_no > 5):
                qoe = float(qoe_obj["QoE2"])
                qoes[ts] = qoe
            chunk_no += 1
    return qoes


if __name__ == '__main__':
    # dataFolder = "D://Data/QDiag/controlled-exps/srv-01/"
    dataFolder = "D://Data/QRank/controlled/server_anomaly/server_anomaly_user_qoes/"
    # date_prefix = "_0221"
    date_prefix = "_062507"

    clients = {
        "A1":"planetlab01.cs.washington.edu",
        "A2":"planetlab02.cs.washington.edu",
        "A3":"planetlab03.cs.washington.edu",
        "A4":"planetlab04.cs.washington.edu",
        "B1":"planetlab1.cs.uoregon.edu",
        "B2":"planetlab3.cs.uoregon.edu",
        "B3":"planetlab4.cs.uoregon.edu",
        "C1":"planetlab1.postel.org",
        "C2":"planetlab4.postel.org"
    }

    '''
    clients = {
        "A1":"planetlab01.cs.washington.edu",
        "A2":"planetlab02.cs.washington.edu",
        "A3":"planetlab04.cs.washington.edu",
        "B2":"planetlab-2.cmcl.cs.cmu.edu",
        "B3":"planetlab-3.cmcl.cs.cmu.edu",
        "C1":"planetlab3.eecs.umich.edu",
        "C2":"planetlab5.eecs.umich.edu"
    }
    '''

    start_ts = 1498374000
    end_ts = start_ts + 3600

    img_name = dataFolder + "qoes_server_anomaly"

    to_plot = {}

    for k,v in clients.iteritems():
        client_file = get_file_by_prefix(dataFolder, v+date_prefix)
        if client_file:
            client_qoes = read_qoe(client_file, start_ts, end_ts)
            to_plot[k] = client_qoes

    plot_qoe_curves(to_plot, start_ts, end_ts, img_name)