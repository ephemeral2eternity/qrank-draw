from draw_anomalies_offline import *

if __name__ == '__main__':
    ##################################################################################################################
    ## Section IV.B, get the anomalous system for QoE anomalies
    ## Table II
    pp = pprint.PrettyPrinter(indent=4)
    #anomalies_stats_per_origin_type = get_anomaly_stats_per_origin_type(session_anomalies)
    #pp.pprint(anomalies_stats_per_origin_type)

    ## Draw QoE anomaly statistics over different access networks as anomalous systems
    # anomalies_stats_per_access_networks = get_anomalies_stats_per_specific_origin_type(session_anomalies, "access_network")
    # pp.pprint((anomalies_stats_per_access_networks))
    '''
    session_anomalies = get_all_anomalous_sessions()
    anomaly_stats_per_origin = draw_anomalies_stats_per_origin_type(session_anomalies, graph="access_network", img_name="all")
    print("Totally there are %d access network ISPs incurring QoE anomalies!" % len(anomaly_stats_per_origin))

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="access_network", img_name="persistent")

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="access_network", img_name="recurrent", top_n=6)

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="access_network", img_name="occasional")
    '''

    session_anomalies = get_all_anomalous_sessions()
    anomaly_stats_per_origin = draw_anomalies_stats_per_origin_type(session_anomalies, graph="transit_network", img_name="all", top_n=9)
    print("Totally there are %d transit network ISPs incurring QoE anomalies!" % len(anomaly_stats_per_origin))

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="transit_network", img_name="persistent", top_n=2)

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="transit_network", img_name="recurrent", top_n=9)

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="transit_network", img_name="occasional", top_n=9)

    session_anomalies = get_all_anomalous_sessions()
    anomaly_stats_per_origin = draw_anomalies_stats_per_origin_type(session_anomalies, graph="device", img_name="all")
    print("Totally there are %d types of devices incurring QoE anomalies!" % len(anomaly_stats_per_origin))

    persistent_session_anomalies = get_persistent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(persistent_session_anomalies, graph="device", img_name="persistent")

    recurrent_session_anomalies = get_recurrent_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(recurrent_session_anomalies, graph="device", img_name="recurrent")

    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    draw_anomalies_stats_per_origin_type(occasional_anomalous_sessions, graph="device", img_name="occasional")