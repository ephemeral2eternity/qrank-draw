import requests
import re
import os
import json
import time
from azure_utils import *
from json_utils import *

################################################################################
## @descr: load json from file
## @params: json_file ---- the full path file name of the json file to be loaded
################################################################################
def loadJson(json_file):
    with open(json_file) as f:
        data = json.loads(f.read())
        return data

#################################################################################
## @descr: Create folder if not exists
## @params: folderPath ---- The folder to create if not exists
#############################################################################
def createFolder(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

#############################################################################
## @descr: Download files from denoted url to the local folder
## @params: url ---- the denoted URL to download the file
##          local_folder ---- the local folder to save the downloaded file
#############################################################################
def downloadFile(url, local_folder):
    rsp = requests.get(url)
    filename_data = re.findall("filename=\"(.+)\"", rsp.headers['content-disposition'])
    filename = filename_data[0]
    full_filename = local_folder + filename

    print("Downloading file %s ..." % filename)

    f = open(full_filename, 'wb')
    for chunk in rsp.iter_content(chunk_size=512*1024):
        if chunk:
            f.write(chunk)
    f.close()

    return

#########################################################################################################
## @descr: Download all sessions' latencies to local folder
## @params: local_folder ---- the local folder to save all sessions' files
##          session_file ---- the json file that contains details of sessions and session ids.
##########################################################################################################
def downloadSessionLatencies(local_folder, session_file):
    session_folder = local_folder + "sessions/"
    createFolder(session_folder)
    session_lat_folder = session_folder + "lats/"
    createFolder(session_lat_folder)

    session_data = loadJson(local_folder+session_file)
    session_ids = session_data.keys()

    lat_url = "http://monitor.cmu-agens.com/dump_latency_json?type=session&id="
    for cur_id in session_ids:
        cur_lat_url = lat_url + cur_id
        downloadFile(cur_lat_url, session_lat_folder)

#########################################################################################################
## @descr: Download all sessions' latencies to local folder
## @params: local_folder ---- the local folder to save all sessions' files
##          session_file ---- the json file that contains details of sessions and session ids.
##########################################################################################################
def downloadNetworkLatencies(local_folder, isps_file):
    networks_folder = local_folder + "networks/"
    createFolder(networks_folder)
    isps_data = loadJson(local_folder+isps_file)

    url = "http://monitor.cmu-agens.com/dump_latency_json?type=network&id="
    for as_num in isps_data.keys():
        networks = isps_data[as_num]["networks"]
        for cur_id in networks.keys():
            cur_url = url + cur_id
            downloadFile(cur_url, networks_folder)


#########################################################################################################
## @descr: Download all sessions' latencies to local folder
## @params: local_folder ---- the local folder to save all sessions' files
##          isps_file ---- the json file that contains details of isps and network ids.
##########################################################################################################
def downloadLinkLatencies(local_folder, links_file):
    links_folder = local_folder + "links/"
    createFolder(links_folder)
    links_data = loadJson(local_folder+links_file)

    url = "http://monitor.cmu-agens.com/dump_latency_json?type=link&id="

    for cur_id in links_data.keys():
        cur_url = url + cur_id
        downloadFile(cur_url, links_folder)
        time.sleep(2)

#####################################################################################
## @params: locator_ip ---- the ip of the cloud agent to get the user data.
##          ts ---- the timestamp from which the QoE for all sessions to be retrieved
## @return: the list include all qoe updates from all session
#####################################################################################
def get_user_devices(locator_ip):
    url = "http://%s/diag/get_all_user_device_json" % locator_ip

    try:
        rsp = requests.get(url)
        return rsp.json()
    except:
        return []

#####################################################################################
## @descr: dump qoes for all sessions to local_folder/sessions/qoes/
#####################################################################################
def dump_all_user_devices(local_folder, device_file="devices.json"):
    # locators = list_locators("agens", "locator-")
    locators = aws_list_locators()

    all_devices_list = []
    unique_devices = []
    for locator in locators:
        locator_ip = locator["ip"]
        locator_name = locator["name"]
        print("Getting user device from locator: " + locator_name)
        user_devices = get_user_devices(locator_ip)
        for user_device in user_devices:
            all_devices_list.extend(user_device)
            if user_device["device"] not in unique_devices:
                unique_devices.append(user_device["device"])

    device_id = 0
    all_devices = {}
    for device in unique_devices:
        related_session_ids = get_device_related_sessions(all_devices_list, device)
        all_devices[device_id] = {}
        all_devices[device_id]["device"] = device
        all_devices[device_id]["related_sessions"] = related_session_ids


    #all_devices = {}
    #for user_device in all_devices_list:
    #    all_devices[user_device["ip"]] = user_device["device"]

    dumpJson(all_devices, local_folder + device_file)

#####################################################################################
## @descr: get all related session ids for a device
#####################################################################################
def get_device_related_sessions(all_devices_list, device_to_cmp):
    device_client_ips = []
    for user_device in all_devices_list:
        if device_to_cmp == user_device["device"]:
            device_client_ips.append(user_device["ip"])

    session_ids = [get_session_id_by_client_ip(client_ip) for client_ip in device_client_ips]
    return session_ids

#####################################################################################
## @descr: get session id by the session's client IP
#####################################################################################
def get_session_id_by_client_ip(client_ip):
    #client_node_id = get_node_by_ip(client_ip)
    #session_id, session = get_session_by_client_id(client_node_id)
    #return session_id



#############################################################################
## @descr: Download all files that are on monitor agent
## @params: local_folder ---- the local folder to save the downloaded file
#############################################################################
def downloadAllMonitor(local_folder):
    base_url = "http://monitor.cmu-agens.com/"

    sessions_download_url = base_url + "dump_all_sessions_json"
    downloadFile(sessions_download_url, local_folder)

    nodes_download_url = base_url + "dump_all_nodes_json"
    downloadFile(nodes_download_url, local_folder)

    links_download_url = base_url + "dump_all_links_json"
    downloadFile(links_download_url, local_folder)

    anomalies_download_url = base_url + "dump_all_anomalies_json"
    downloadFile(anomalies_download_url, local_folder)

    isps_download_url = base_url + "dump_all_isps_json"
    downloadFile(isps_download_url, local_folder)

    networks_download_url = base_url + "dump_all_networks_json"
    downloadFile(networks_download_url, local_folder)

    downloadSessionLatencies(local_folder, "sessions.json")
    downloadNetworkLatencies(local_folder, "isps.json")
    downloadLinkLatencies(local_folder, "links.json")

    dump_all_user_devices(local_folder, device_file="devices.json")

if __name__ == '__main__':
    # dataFolder = "D://Data//QRank//20170712//"
    dataFolder = "/Users/chenw/Data/QRank/20170712/"
    dump_all_user_devices(dataFolder)
    # downloadAllMonitor(dataFolder)
    # downloadLinkLatencies(dataFolder, "links.json")
    # base_url = "http://monitor.cmu-agens.com/"
    # anomalies_download_url = base_url + "dump_all_anomalies_json"
    # downloadFile(anomalies_download_url, dataFolder)







