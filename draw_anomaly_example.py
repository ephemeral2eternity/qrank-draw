import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO
from json_utils import *
import pprint
from fig_utils import *
from drawlibs.plot_qoe_curves import *
from drawlibs.draw_for_anomaly import *
import numpy as np
from get_objects import *


#####################################################################################
## @descr: Plot the qoes values within an anomaly period
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the anomalous period
#####################################################################################
def plot_qoes_for_anomaly(session_id, anomaly_id):
    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    # pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period
    session_id = anomaly["session_id"]

    session_qoes = get_session_qoes_in_range(session_id, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_qoes"
    draw_qoes_for_anomaly(session_qoes, draw_start, draw_end, anomaly_start, anomaly_end, img_name, num_intvs=5)

#####################################################################################
## @descr: Plot the probed latencies for all networks involved in a session in
##         an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_network_lats_for_anomaly(session_id, anomaly_id, agent="planetlab"):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    network_ids = get_networks_by_session(session)
    networks_details = {}
    for network_id in network_ids:
        networks_details[network_id] = get_network(network_id)

    networks_lats = {}
    networks_lats_stats = []
    for network_id in network_ids:
        networks_lats[network_id] = get_network_lats_in_range(network_id, draw_start, draw_end, agent)
        cur_network_lats_stats = get_lats_stat_in_anomaly(networks_lats[network_id], anomaly_start, anomaly_end)
        cur_network_lats_stats["network"] = networks_details[network_id]["name"] \
                                            + "(AS " + str(networks_details[network_id]["as"]) + ")" \
                                            + "@(" + str(networks_details[network_id]["latitude"]) + "," \
                                            + str(networks_details[network_id]["longitude"]) + ")"
        networks_lats_stats.append(cur_network_lats_stats)

    json2csv(networks_lats_stats, rstsfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_nets_lats_" + agent + ".csv")

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_nets_lats_" + agent
    draw_networks_lats_for_anomaly(networks_lats, networks_details, draw_start, draw_end, anomaly_start, anomaly_end, img_name)

#####################################################################################
## @descr: Plot the latencies probed by traceroute for all links in a session
##         within an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_link_lats_for_anomaly(session_id, anomaly_id):
    session = get_objects(datafolder + session_file, [session_id])[0]

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    link_objs = session["links"]
    link_ids = link_objs.keys()

    link_details = get_link_details(link_objs)
    link_lats = get_link_lats_in_range(link_ids, draw_start, draw_end)

    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_link_lats"
    draw_links_lats_for_anomaly(link_lats, link_details, draw_start, draw_end, anomaly_start, anomaly_end, img_name)

#####################################################################################
## @descr: Plot the session latencies in an anomalous period denoted by the anomaly_id
## @params: anomaly_id --- the id of the anomaly to study the anomalous period
##          session_id --- the id of the session to study the involved networks
#####################################################################################
def plot_session_lat_for_anomaly(session_id, anomaly_id):
    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    # pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period
    session_id = anomaly["session_id"]
    session = get_objects(datafolder + session_file, [session_id])[0]

    session_lats = get_session_lats_in_range(session_id, draw_start, draw_end)
    img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_lats"
    draw_session_lats_for_anomaly(session_lats, draw_start, draw_end, anomaly_start, anomaly_end, img_name)
    session_lats_stats = get_lats_stat_in_anomaly(session_lats, anomaly_start, anomaly_end)
    session_lats_stats["session_id"] = session_id

    json2csv([session_lats_stats], rstsfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_session_lats.csv")

#####################################################################################
## @descr: Get a list of node ids for all nodes in a given session
## @params: session_id --- the id of the session to study get the nodes
#####################################################################################
def get_all_nodes_by_session(session_id):
    session = get_objects(datafolder + session_file, [session_id])[0]
    hops = session["hops"]

    unique_nodes = []
    for hop_seq in hops.keys():
        hop_nodes = hops[hop_seq]
        for node_id in hop_nodes:
            if node_id not in unique_nodes:
                unique_nodes.append(node_id)

    return unique_nodes

#####################################################################################
## @descr: Get a list of related session ids that share one or more nodes with the given session
## @params: session_id --- the id of the session to obtain the related session ids
#####################################################################################
def get_related_sessions(session_id):
    node_ids = get_all_nodes_by_session(session_id)
    unique_sessions = []
    for node_id in node_ids:
        node = get_objects(datafolder + node_file, node_id)
        related_session_ids = node["related_sessions"]
        for related_session_id in related_session_ids:
            if related_session_id not in unique_sessions:
                unique_sessions.append(related_session_id)

    if session_id not in unique_sessions:
        unique_sessions.append(session_id)
    return unique_sessions

#####################################################################################
## @descr: Get a list of related session ids that share one or more nodes with the given session
## @params: session_id --- the id of the session to obtain the related session ids
#####################################################################################



if __name__ == '__main__':

    session_id = 81
    anomaly_id = 5778

    ## Ploting params
    pp = pprint.PrettyPrinter(indent=4)

    anomaly = get_anomaly(session_id, anomaly_id)
    anomaly_start = float(anomaly["start"])
    anomaly_end = float(anomaly["end"])
    pp.pprint(anomaly)

    draw_start = anomaly_start - period
    draw_end = anomaly_start + period

    session_id = anomaly["session_id"]

    plot_qoes_for_anomaly(session_id, anomaly_id)
    plot_network_lats_for_anomaly(session_id, anomaly_id, agent="azure")
    plot_link_lats_for_anomaly(session_id, anomaly_id)
    plot_session_lat_for_anomaly(session_id, anomaly_id)

    #session = get_objects(datafolder+session_file, [session_id])[0]
    # pp.pprint(session)
    # session_qoes = get_session_qoes_in_range(qoesfolder, session_id, draw_start, draw_end)

    #img_name = imgfolder + "anomaly_" + str(anomaly_id) + "_session_" + str(session_id) + "_qoes"

    #network_ids = get_networks_by_session(session)
    # pp.pprint(network_ids)