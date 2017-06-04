import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from json_utils import *

## Get anomaly details by anomaly_id
def get_anomaly(all_anomalies_file, anomaly_id):
    all_anomalies = loadJson(all_anomalies_file)
    anomaly = all_anomalies[str(anomaly_id)]
    return anomaly


if __name__ == '__main__':
    datafolder = "/Users/chenw/Data/QRank/20170510/"
    qoesfolder = datafolder + "sessions/qoes/"
    linksfolder = datafolder + "links/"
    networksfolder = datafolder + "networks/"

    # datafolder = "D://Data/QRank/20170510/"
    anomaly_file = "anomalies.json"
    session_file = "sessions.json"
    anomaly_id_to_draw = 190

    anomaly = get_anomaly(datafolder+anomaly_file, anomaly_id_to_draw)

    print(anomaly)
    session_id = anomaly["session_id"]
