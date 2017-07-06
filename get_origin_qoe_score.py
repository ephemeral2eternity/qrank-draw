from json_utils import *
from get_objects import *
import pandas as pd


def get_origin_qoe_score(origin_session_ids, time_range):
    origin_qoes = []
    for session_id in origin_session_ids:
        session_qoes = get_session_qoes_in_range(session_id, time_range[0], time_range[1])
        session_qoes_pd = pd.DataFrame(session_qoes)
        session_qoe_ave = session_qoes_pd["QoE"].mean()
        print("The QoE average for session " + str(session_id) + " is " + str(session_qoe_ave))
        origin_qoes.append(session_qoe_ave)

    origin_qoe_score = sum(origin_qoes) / float(len(origin_qoes))
    return origin_qoe_score


if __name__ == '__main__':
    # origin_session_ids = [22, 44, 77]
    origin_session_ids = [22, 44]
    ts_range = [1496559660, 1496560260]

    origin_qoe_score = get_origin_qoe_score(origin_session_ids, ts_range)
    print(origin_qoe_score)