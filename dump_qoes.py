from dump_monitor_data import *
from azure_utils import *
from json_utils import *

#####################################################################################
## @descr: get the session id from monitor
## @params: client ---- client ip of the session
##          server ---- server ip of the session
## @return: session id on the monitor agent (monitor.cmu-agens.com)
#####################################################################################
def get_session_id(client, server):
    url = "http://monitor.cmu-agens.com/get_session_json?client=%s&server=%s" % (client, server)

    try:
        rsp = requests.get(url)
        session_json = rsp.json()
        # print(session_json)
        return int(session_json['id'])
    except:
        return -1


#####################################################################################
## @params: locator_ip ---- the ip of the locator to get the QoE data.
##          ts ---- the timestamp from which the QoE for all sessions to be retrieved
## @return: the list include all qoe updates from all session
#####################################################################################
def get_qoes(locator_ip, ts=None):
    if ts:
        url = "http://%s/diag/get_all_qoes_json?ts=%s" % (locator_ip, ts)
    else:
        url = "http://%s/diag/get_all_qoes_json" % locator_ip
    try:
        rsp = requests.get(url)
        return rsp.json()
    except:
        return []

#####################################################################################
## @descr: collect QoE updates from all locators
#####################################################################################
def get_all_qoes():
    locators = list_locators("agens", "locator-")

    all_qoes = []
    for locator in locators:
        locator_ip = locator["ip"]
        locator_name = locator["name"]
        print("Getting QoE updates from locator: " + locator_name)
        qoes = get_qoes(locator_ip)
        all_qoes.extend(qoes)
    return all_qoes


#####################################################################################
## @descr: dump qoes for all sessions to local_folder/sessions/qoes/
#####################################################################################
def dump_all_qoes(local_folder):
    session_folder = local_folder + "sessions/"
    createFolder(session_folder)
    session_qoe_folder = session_folder + "qoes/"
    createFolder(session_qoe_folder)

    all_qoes = get_all_qoes()
    null_count = 1

    for session_qoes in all_qoes:
        session_id = get_session_id(session_qoes['client'], session_qoes['server'])
        file_name = session_qoe_folder + "session_" + str(session_id) + "_qoes.json"
        if session_id < 0:
            file_name = session_qoe_folder + "session_N" + str(null_count) + "_qoes.json"
            null_count += 1

        dumpJson(session_qoes, file_name)


if __name__ == '__main__':
    # dataFolder = "D://Data//QRank//20170510//"
    dataFolder = "/Users/chenw/Data/QRank/20170610/"
    dump_all_qoes(dataFolder)

    #client = "139.80.206.133"
    #server = "117.18.232.200"
    #session_id = get_session_id(client, server)
    # print(session_id)
