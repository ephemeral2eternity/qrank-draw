import glob
import os
import re
from data_folder import *
from get_objects import *

def get_anomalous_sessions():
    all_session_anomaly_files = glob.glob(qrankfolder + "session_*")
    for session_file in all_session_anomaly_files:
        session_file_name = os.path.basename(session_file)
        session_id = re.findall(r'\d+', session_file_name)[0]
        session_obj = get_session(session_id)
        server = get_node(session_obj[""])




#####################################################################################
## @descr: analyze QoE anomalies from all sessions
## that locates the anomalies over the origin type
#####################################################################################
if __name__ == '__main__':
    ## Get the # of anomalous sessions from PlanetLab users
    anomalous_sessions = get_anomalous_sessions()
