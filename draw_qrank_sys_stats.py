import glob
from data_folder import *
from json_utils import *
import pprint
from get_objects import *

#####################################################################################
## @descr: Analyze anomalies per device type
## @return: anomaly_cnt_per_device_type ---- get the count of anomalies per anomalous system types
#####################################################################################
def analyze_anomalous_device_types():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    anomaly_cnt_per_device_type = {}
    anomaly_period_per_device_type = {}
    ave_anomaly_period_per_device_type = {}
    for session_anomaly_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_anomaly_file)
        for anomaly in session_anomalies:
            anomaly_period = anomaly["end"] - anomaly["start"]
            for anomaly_sys in anomaly["anomaly_system"]:
                if anomaly_sys["type"] == "device":
                    device_type = str(anomaly_sys["obj"]["device"])
                    if device_type not in anomaly_cnt_per_device_type.keys():
                        anomaly_cnt_per_device_type[device_type] = 0
                        anomaly_period_per_device_type[device_type] = []
                    anomaly_cnt_per_device_type[device_type] += 1
                    anomaly_period_per_device_type[device_type].append(anomaly_period)

    for device_type in anomaly_period_per_device_type.keys():
        ave_anomaly_period_per_device_type[device_type] = np.mean(anomaly_period_per_device_type[device_type])
    return anomaly_cnt_per_device_type, ave_anomaly_period_per_device_type


#####################################################################################
## @descr: Read anomalies from qrank folder and gets the anomaly system types
## @return: anomaly_cnt_per_system_type ---- get the count of anomalies per anomalous system types
## ave_anomaly_period_per_system_type ---- get the average period of anomalies per system types
#####################################################################################
def analyze_anomalous_system_types():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    anomalous_session_num = len(all_session_anomaly_files)
    print("There are totally %d users having QoE anomalies!" % anomalous_session_num)
    anomaly_cnts_per_system_type = {
        "total": 0,
        "device": 0,
        "server": 0,
        "network": 0,
        "access_network": 0,
        "transit_network": 0,
        "cloud_network": 0
    }

    anomaly_period_per_system_type = {
        "total": [],
        "device": [],
        "server": [],
        "network": [],
        "access_network": [],
        "transit_network": [],
        "cloud_network": []
    }

    ave_anomaly_period_per_system_type = {
        "total": 0,
        "device": 0,
        "server": 0,
        "network": 0,
        "access_network": 0,
        "transit_network": 0,
        "cloud_network": 0
    }
    for session_anomaly_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_anomaly_file)
        network_anomaly = False
        for anomaly in session_anomalies:
            system_is_anomaly = {
                "access_network": False,
                "transit_network": False,
                "cloud_network": False,
                "network": False,
                "device": False,
                "server": False,
                "total": True
            }
            for anomaly_sys in anomaly["anomaly_system"]:
                if anomaly_sys["type"] != "network":
                    cur_sys_type = anomaly_sys["type"]
                else:
                    system_is_anomaly["network"] = True
                    network_type = anomaly_sys["obj"]["type"]
                    cur_sys_type = network_type + "_network"
                system_is_anomaly[cur_sys_type] = True

            anomaly_period = anomaly["end"] - anomaly["start"]
            for system_type in system_is_anomaly.keys():
                if system_is_anomaly[system_type]:
                    anomaly_cnts_per_system_type[system_type] += 1
                    anomaly_period_per_system_type[system_type].append(anomaly_period)

    for sys_type in anomaly_period_per_system_type.keys():
        ave_anomaly_period_per_system_type[sys_type] = np.mean(anomaly_period_per_system_type[sys_type])

    return anomaly_cnts_per_system_type, ave_anomaly_period_per_system_type

#####################################################################################
## @descr: Read anomalies from qrank folder and gets the anomaly of denoted types
## @return: cnts_per_node_type ---- get the count of requested anomalies per device node types
## ave_anomaly_period_per_node_type ---- get the average period of requested anomalies per device node types
#####################################################################################
def analyze_anomalies_per_node_type(anomaly_type="all"):
    anomaly_cnt_per_node_type = {}
    anomaly_period_per_node_type = {}
    ave_anomaly_period_per_node_type = {}
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    for session_anomaly_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_anomaly_file)
        for anomaly in session_anomalies:
            anomaly_session_id = anomaly["session_id"]
            if anomaly_type == "all":
                device = get_device_by_session_id(anomaly_session_id)
                cur_node_type = device["device"]["device"]
                anomaly_duration = anomaly["end"] - anomaly["start"]
                # print("%s node type with duration %d seconds" % (cur_node_type, anomaly_duration))
                if cur_node_type not in anomaly_cnt_per_node_type.keys():
                    anomaly_cnt_per_node_type[cur_node_type] = 0
                    anomaly_period_per_node_type[cur_node_type] = []
                anomaly_cnt_per_node_type[cur_node_type] += 1
                anomaly_period_per_node_type[cur_node_type].append(anomaly_duration)
            else:
                anomaly_match = False
                for anomaly_sys in anomaly["anomaly_system"]:
                    if anomaly_sys["type"] != "network":
                        if anomaly_sys["type"] == anomaly_type:
                            anomaly_match = True
                    else:
                        network_type = anomaly_type.split("_")[0]
                        if anomaly_sys["obj"]["type"] == network_type:
                            anomaly_match = True

                if anomaly_match:
                    device = get_device_by_session_id(anomaly_session_id)
                    cur_node_type = device["device"]["device"]
                    anomaly_duration = anomaly["end"] - anomaly["start"]
                    # print("%s node type with duration %d seconds" % (cur_node_type, anomaly_duration))
                    if cur_node_type not in anomaly_cnt_per_node_type.keys():
                        anomaly_cnt_per_node_type[cur_node_type] = 0
                        anomaly_period_per_node_type[cur_node_type] = []
                    anomaly_cnt_per_node_type[cur_node_type] += 1
                    anomaly_period_per_node_type[cur_node_type].append(anomaly_duration)

    for node_type in anomaly_period_per_node_type.keys():
        ave_anomaly_period_per_node_type[node_type] = np.mean(anomaly_period_per_node_type[node_type])

    return anomaly_cnt_per_node_type, ave_anomaly_period_per_node_type



if __name__ == '__main__':
    ## Get the statistics of anomalies per system type
    anomaly_cnts_per_system_type, ave_anomaly_period_per_system_type = analyze_anomalous_system_types()
    pp = pprint.PrettyPrinter(indent=4)
    print("The anomaly counts per system type is as follows:")
    pp.pprint(anomaly_cnts_per_system_type)
    dumpJson(anomaly_cnts_per_system_type, rstsfolder + "anomaly_cnts_per_system_type.json")
    print("The average anomaly period per system type is as follows:")
    pp.pprint(ave_anomaly_period_per_system_type)
    dumpJson(ave_anomaly_period_per_system_type, rstsfolder + "ave_anomaly_period_per_system_type.json")


    ## Get the statistics of anomalies per device type
    anomaly_cnts_per_device_type, ave_anomaly_period_per_device_type = analyze_anomalous_device_types()
    print("The anomaly counts per device type is as follows:")
    pp.pprint(anomaly_cnts_per_device_type)
    dumpJson(anomaly_cnts_per_device_type, rstsfolder + "anomaly_cnts_per_device_type.json")
    print("The average anomaly period per device type is as follows:")
    pp.pprint(ave_anomaly_period_per_device_type)
    dumpJson(ave_anomaly_period_per_device_type, rstsfolder + "ave_anomaly_period_per_device_type.json")

    ## Analyze the percentage of anomalies that are identified in access networks for Planetlab nodes
    cnts_per_node_type, ave_anomaly_period_per_node_type = analyze_anomalies_per_node_type(anomaly_type="access_network")
    print("The anomaly counts per node type is as follows:")
    pp.pprint(cnts_per_node_type)
    dumpJson(cnts_per_node_type, rstsfolder + "access_network_anomaly_cnts_per_node_type.json")
    print("The average anomaly period per node type is as follows:")
    pp.pprint(ave_anomaly_period_per_node_type)
    dumpJson(ave_anomaly_period_per_node_type, rstsfolder + "ave_access_network_anomaly_period_per_node_type.json")

    ## Analyze the percentage of anomalies that are identified in access networks for Planetlab nodes
    cnts_per_node_type, ave_anomaly_period_per_node_type = analyze_anomalies_per_node_type(anomaly_type="device")
    print("The anomaly counts per node type is as follows:")
    pp.pprint(cnts_per_node_type)
    dumpJson(cnts_per_node_type, rstsfolder + "device_anomaly_cnts_per_node_type.json")
    print("The average anomaly period per node type is as follows:")
    pp.pprint(ave_anomaly_period_per_node_type)
    dumpJson(ave_anomaly_period_per_node_type, rstsfolder + "ave_device_anomaly_period_per_node_type.json")