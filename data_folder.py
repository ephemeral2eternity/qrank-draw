## Configure the data folders
datafolder = "D:/Data/QRank/20170610/"
# datafolder = "/Users/chenw/Data/QRank/20170510/"

imgfolder = datafolder + "imgs/"
rstsfolder = datafolder + "rsts/"
qoesfolder = datafolder + "sessions/qoes/"
latsfolder = datafolder + "sessions/lats/"
linksfolder = datafolder + "links/"
networksfolder = datafolder + "networks/"

# datafolder = "D://Data/QRank/20170510/"
anomaly_file = "merged_anomalies_revised.json"
session_file = "sessions.json"
node_file = "nodes.json"
network_file = "networks.json"

## Parameters to detect QoE anomalies and to merge QoE anomalies
period = 300
qoe_th = 2
intvl_th = 12
intvl_seconds_th = 60
top_n = 10