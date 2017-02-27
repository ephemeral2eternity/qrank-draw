import glob
import ntpath
import re
import json
import copy
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
# from pylab import *
import matplotlib.lines as mlines

def json2nxgraph(graph_json):
    nodes = graph_json["nodes"]
    links = graph_json["links"]
    route_graph = nx.Graph()

    node_ids = []
    labels = {}
    for node in nodes:
        if node["type"] == "server":
            if node["suspect"] == "true":
                route_graph.add_node(node["id"], node_shape='s', node_size=300, node_color='r')
            else:
                route_graph.add_node(node["id"], node_shape='s', node_size=300, node_color='b')
            labels[node["id"]] = node["name"]
        elif node["type"] == "client":
            if node["suspect"] == "true":
                route_graph.add_node(node["id"], node_shape='^', node_size=200, node_color='r')
            else:
                route_graph.add_node(node["id"], node_shape='^', node_size=200, node_color='m')
            labels[node["id"]] = node["name"]
        else:
            if node["suspect"] == "true":
                route_graph.add_node(node["id"], node_shape='o', node_size=50, node_color='r')
            else:
                route_graph.add_node(node["id"], node_shape='o', node_size=50, node_color='grey')
        node_ids.append(node["id"])

    for link in links:
        if link["group"] == "intra":
            route_graph.add_edge(node_ids[link["source"]], node_ids[link["target"]], edge_color='k', edge_weight=0.5)
        else:
            route_graph.add_edge(node_ids[link["source"]], node_ids[link["target"]], edge_color='b', edge_weight=2.0)

    return route_graph, labels


def draw_network_graph(graph_obj, isLabel=False, labels=None, toSave=False, figName="network_graph"):
    # pos=nx.spring_layout(graph_obj, k=0.4, iterations=200)
    pos = nx.graphviz_layout(graph_obj, prog="neato", args="-Tps -Gsplines=true -Goverlap=scalexy -Gepsilon=2")
    # pos = nx.graphviz_layout(graph_obj, prog="neato", args="-Tps -Gsplines=true -Goverlap=scalexy -Gepsilon=5")

    f, ax = plt.subplots()

    if isLabel:
        #for labeling outside the node
        offset = 0.05
        pos_labels = {}
        keys = pos.keys()
        for key in keys:
            x, y = pos[key]
            pos_labels[key] = (x+2*offset, y-offset)
        nx.draw_networkx_labels(graph_obj, pos=pos_labels, labels=labels, fontsize=5, font_color='k')

    #Get all distinct node classes according to the node shape attribute
    nodeShapes = set((aShape[1]["node_shape"] for aShape in graph_obj.nodes(data=True)))

    p_handlers = {}
    for aShape in nodeShapes:
        curNodesDict = [sNode for sNode in filter(lambda x: x[1]["node_shape"] == aShape,graph_obj.nodes(data = True))]
        curNodes = [cNode[0] for cNode in curNodesDict]
        nodesizelist = [cNode[1]["node_size"] for cNode in curNodesDict]
        # print nodesizelist
        nodecolorlist = [cNode[1]["node_color"] for cNode in curNodesDict]
        # print nodecolorlist
        p_handlers[aShape] = nx.draw_networkx_nodes(graph_obj, pos, node_shape=aShape, nodelist=curNodes, node_size=nodesizelist, node_color=nodecolorlist, alpha = 0.5)
        #nx.draw_networkx_nodes(graph_obj, pos, node_shape=aShape, nodelist=curNodes, alpha = 0.5)

    edge_colors = [curEdge[2]["edge_color"] for curEdge in graph_obj.edges(data = True)]
    edge_weights = [curEdge[2]["edge_weight"] for curEdge in graph_obj.edges(data=True)]
    nx.draw_networkx_edges(graph_obj, pos, edge_color=edge_colors, width=edge_weights)
    # nx.draw_networkx_edges(graph_obj, pos)
    # print graph_obj.edges(data = True)

    #orange_patch = mpatches.Patch(color='r', label='Suspect', alpha=0.5)
    red_patch = mpatches.Patch(color='r', label='Suspect', alpha=0.5)
    #green_patch = mpatches.Patch(color='g', label='Good', alpha=0.5)
    p_lg = [p_handlers[x] for x in ['^', 'o', 's']]
    lnintra = mlines.Line2D([], [], color='black', linewidth=0.5, label='Intra ISP')
    lninter = mlines.Line2D([], [], color='blue', linewidth=2.0, label='Inter ISP')
    #p_lg.append(green_patch)
    p_lg.append(red_patch)
    p_lg.append(lnintra)
    p_lg.append(lninter)
    plt.legend(p_lg, ["Clients","Routers", "Servers", "Suspect", "Intra ISP", "Inter ISP"], loc=4)
    plt.axis('off')
    # nx.draw_networkx(graph_obj, pos)
    plt.show()

    if toSave:
        save_fig(f, figName)

def save_fig(fig, figName, figFolder = "./imgs/"):
    pdf = PdfPages(figFolder + figName + '.pdf')
    pdf.savefig(fig)
    fig.savefig(figFolder + figName+'.png', dpi=600, format='png')
    pdf.close()

if __name__ == '__main__':
    # dataFolder = "D://Data/QDiag/controlled-exps/"
    dataFolder = "/Users/chenw/Data/QDiag/controlled-exps/"
    # graph_file = "controlled-exp-graph.json"
    graph_file = "srv-fault-graph.json"

    with open(dataFolder + graph_file, 'r') as f:
        graph_json = json.load(f)

        nx_graph, node_labels = json2nxgraph(graph_json)
        draw_network_graph(nx_graph, isLabel=True, labels=node_labels)


