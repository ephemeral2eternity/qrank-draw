## Configure the data folders
datafolder = "D:/Data/QRank/20170719/"
# datafolder = "/Users/chenw/Data/QRank/20170719/"

imgfolder = datafolder + "imgs/"
rstsfolder = datafolder + "rsts/"
qoesfolder = datafolder + "sessions/qoes/"
latsfolder = datafolder + "sessions/lats/"
linksfolder = datafolder + "links/"
networksfolder = datafolder + "networks/"
qrankfolder = datafolder + "qrank/"
raw_monitor_folder = datafolder + "raw/monitor/"
raw_qoes_folder = datafolder + "raw/qoes/"
probed_folder = datafolder + "probed/"

# datafolder = "D://Data/QRank/20170510/"
anomaly_file = "merged_anomalies_revised.json"
session_file = "sessions.json"
node_file = "nodes.json"
device_file = "devices.json"
network_file = "networks.json"
qrank_anomaly_file = "qrank_anomalies.json"

## Parameters to detect QoE anomalies and to merge QoE anomalies
period = 600
qoe_th = 2
intvl_th = 12
intvl_seconds_th = 60
top_n = 10
max_anomaly_duration = 3600
persistent_anomaly_len_th = 900
recurrent_cnt_th = 100

## Parameters for QoE anomaly localization
locate_time_window = 60