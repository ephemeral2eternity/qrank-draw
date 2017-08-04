from draw_anomalies_offline import *

if __name__ == '__main__':

    ##################################################################################################################
    ## Section IV.A, get the prevalence of QoE anomalies
    total_anomalous_sessions = get_all_anomalous_sessions()
    session_anomaly_stats = plot_anomalies_per_session(total_anomalous_sessions, 'total_count', "total_sessions", 10, False)
    dumpJson(session_anomaly_stats, rstsfolder + "anomalies_per_session_stats.json")

    ## Get the number of total anomalous sessions
    anomalous_session_cnt = len(session_anomaly_stats)
    print("There are totally %d anomalous sessions!" % anomalous_session_cnt)

    ## Get the total number of anomalies per type
    df = pd.DataFrame(session_anomaly_stats)
    all_anomalies_count = sum(df['total_count'].values.tolist())
    severe_anomalies_count = sum(df['severe_count'].values.tolist())
    medium_anomalies_count = sum(df['medium_count'].values.tolist())
    light_anomalies_count = sum(df['light_count'].values.tolist())
    print("Among %d QoE anomalies totally, there are %d severe QoE anomalies, %d medium QoE anomalies and %d light QoE anomalies."
          % (all_anomalies_count, severe_anomalies_count, medium_anomalies_count, light_anomalies_count))

    ## Get the number of users who experience persistent QoE anomalies.
    persistent_anomalous_sessions = get_persistent_anomalous_sessions()
    print("There are %d sessions with persistent QoE anomalies!" % len(persistent_anomalous_sessions.keys()))
    persistent_session_anomaly_stats = plot_anomalies_per_session(persistent_anomalous_sessions, "total_count", "persistent_sessions", 6, False)

    ## Get the number of users who experience QoE anomalies recurrently
    recurrent_anomalous_sessions = get_recurrent_anomalous_sessions()
    print("There are %d sessions with recurrent QoE anomalies!" % len(recurrent_anomalous_sessions.keys()))
    recurrent_session_anomaly_stats = plot_anomalies_per_session(recurrent_anomalous_sessions, "total_count", "recurrent_sessions",4, False)

    ## Get the number of users who experience QoE anomalies recurrently
    occasional_anomalous_sessions = get_occasional_anomalous_sessions()
    print("There are %d sessions with occasional QoE anomalies!" % len(occasional_anomalous_sessions.keys()))
    recurrent_session_anomaly_stats = plot_anomalies_per_session(occasional_anomalous_sessions, "total_count", "total_occasional_sessions", 10, False)