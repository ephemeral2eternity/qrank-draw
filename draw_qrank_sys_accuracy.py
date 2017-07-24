import glob
from data_folder import *
from get_file import *
from json_utils import *
from drawlibs.draw_cdf import *

#####################################################################################
## @descr: Read anomalies from qrank folder and gets the accuracy for each anomaly
## @return: all_accuracy: qrank and qwatch accuracy for all anomalies
#####################################################################################
def get_qrank_accuracy():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    all_accuracy = []
    for session_anomaly_file in all_session_anomaly_files:
        session_anomalies = loadJson(session_anomaly_file)
        for anomaly in session_anomalies:
            anomaly_start = anomaly["start"]
            anomaly_end = anomaly["end"]
            suspect_system_size = len(anomaly["qrank"])
            anomaly_system_size = len(anomaly["anomaly_system"])
            session_id = anomaly["session_id"]
            all_accuracy.append({"start": anomaly_start, "end": anomaly_end,
                                 "qrank": anomaly_system_size, "qwatch": suspect_system_size,
                                 "session_id": session_id})

    return all_accuracy

#####################################################################################
## @descr: Analyze the QRank accuracy by the number of anomalies
## @return: list of accuracy for QRank and QWatch
#####################################################################################
def analyze_accuracy():
    all_accuracy = get_qrank_accuracy()
    # dumpJson(all_accuracy, datafolder + "qrank_accuracy.json")

    total_anomalies = len(all_accuracy)

    total_identified = 0
    identification_accuracy_ratio = []
    qrank_accuracy = []
    qwatch_accuracy = []
    for anomaly_accuracy in all_accuracy:
        if anomaly_accuracy["qrank"] == 1:
            total_identified += 1
        qrank_vs_qwatch = anomaly_accuracy["qrank"] / float(anomaly_accuracy["qwatch"])
        qwatch_accuracy.append(anomaly_accuracy["qwatch"])
        qrank_accuracy.append(anomaly_accuracy["qrank"])
        identification_accuracy_ratio.append(qrank_vs_qwatch)

    ## The total number of anomalies and the number of anomalies that has identified at unique system
    print("Among %d anomalies, there are %d anomalies identified at an unique anomalous system!" % (total_anomalies, total_identified))

    ave_accuracy_improvement = np.mean(identification_accuracy_ratio)
    print("On average, the QRank narrows the number of anomalous systems down to %.5f over the number of suspect systems located by QWatch!" % ave_accuracy_improvement)
    return qrank_accuracy, qwatch_accuracy

#####################################################################################
## @descr: Draw the system accuracy CDF for QRank and QWatch
#####################################################################################
def draw_qrank_accuracy():
    qrank_accuracy, qwatch_qccuracy = analyze_accuracy()
    fig, ax = plt.subplots()
    draw_cdf(qrank_accuracy, 'k-', 'QRank')
    draw_cdf(qwatch_qccuracy, 'b-.', 'QWatch')
    ax.set_xlabel(r'The number of systems identified for anomalies', fontsize=12)
    ax.set_ylabel(r'The percentage of users', fontsize=12)
    ax.set_title('The CDF of QRank/QWatch accuracy', fontsize=14)
    plt.legend()

    img_name = imgfolder + "qrank_accuracy_cdf"
    fig.savefig(img_name + ".pdf")
    fig.savefig(img_name + ".jpg")
    fig.savefig(img_name + ".png")

    plt.show()

if __name__ == '__main__':
    draw_qrank_accuracy()



