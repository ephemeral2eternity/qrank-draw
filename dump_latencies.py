import requests
import re
import os
import json

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
    session_folder = local_folder + "sessions//"
    createFolder(session_folder)
    session_data = loadJson(local_folder+session_file)
    session_ids = session_data.keys()

    url = "http://monitor.cmu-agens.com/dump_latency_json?type=session&id="
    for cur_id in session_ids:
        cur_url = url + cur_id
        downloadFile(cur_url, session_folder)

#########################################################################################################
## @descr: Download all sessions' latencies to local folder
## @params: local_folder ---- the local folder to save all sessions' files
##          session_file ---- the json file that contains details of sessions and session ids.
##########################################################################################################
def downloadNetworkLatencies(local_folder, isps_file):
    networks_folder = local_folder + "networks//"
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
    links_folder = local_folder + "links//"
    createFolder(links_folder)
    links_data = loadJson(local_folder+links_file)

    url = "http://monitor.cmu-agens.com/dump_latency_json?type=link&id="

    for cur_id in links_data.keys():
        cur_url = url + cur_id
        downloadFile(cur_url, links_folder)

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

    downloadSessionLatencies(local_folder, "sessions.json")
    downloadNetworkLatencies(local_folder, "isps.json")
    downloadLinkLatencies(local_folder, "links.json")

if __name__ == '__main__':
    dataFolder = "D://Data//QRank//20170509//"
    downloadAllMonitor(dataFolder)





