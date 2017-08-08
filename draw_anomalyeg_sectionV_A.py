from draw_anomaly_example_offline import *

if __name__ == '__main__':
    ## Merge all raw probed latency files into a json file per session
    merge_all_network_lats()


    ## Section V.A 1), Figure 8 (d)
    session_id = 27
    anomaly_ts = 1499763730
    plot_link_lats_for_anomaly(session_id, anomaly_ts)


    ## Section V.A 1), Figure 8 (c)
    #pp = pprint.PrettyPrinter(indent=4)
    session_id = 27

    anomaly_ts = 1499763730
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMean")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMin")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMax")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttStd")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttLoss")

    ## Draw the QoE curve
    plot_qoes_for_anomaly(session_id, anomaly_ts)

    ## Section V.A 2), Figure 10 (d)
    # session_id = 9
    # anomaly_ts = 1499760600

    session_id = 77
    anomaly_ts = 1499940345
    plot_qoes_for_anomaly(session_id, anomaly_ts)

    plot_link_lats_for_anomaly(session_id, anomaly_ts)

    ## Section V.A 1), Figure 8 (c)
    #pp = pprint.PrettyPrinter(indent=4)

    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMean")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMin")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttMax")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttStd")
    plot_probed_lats_for_anomaly(session_id, anomaly_ts, rttToDraw="rttLoss")