import datetime
import pytz
import untangle
import os
from aecms.settings import EXTERNAL_DIR, TIME_ZONE
from .common_verdicts import EJUDGE_TO_GLOBAL
from lib.judges.main.global_verdicts import *

def localize_time(time_str):
    try:
        time_dt = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
    except:
        time_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    time_dt = pytz.timezone(TIME_ZONE).localize(time_dt)
    return time_dt.astimezone(pytz.timezone('UTC')).timestamp()


def load_ejudge_contest(contest_id, ejudge_ids):
    ejudge_id = '{:06d}'.format(contest_id)
    try:
        data = untangle.parse(os.path.join(EXTERNAL_DIR, ejudge_id, 'dir/external.xml'))
    except:
        return None

    problems = [{
        'id': problem['id'],
        'long': problem['long_name'],
        'short': problem['short_name'],
        'index': index,
    } for index, problem in enumerate(data.runlog.problems.children)]

    problem_index = {problem['id']: problem['index'] for problem in problems}

    runs_list = []

    for run in data.runlog.runs.children:
        try:
            ejudge_id = int(run['user_id'])
            status = EJUDGE_TO_GLOBAL[run['status']]
            time = int(run['time'])

            user_id = ejudge_ids[ejudge_id]

            prob_id = problem_index[run['prob_id']]
            score = (1 if status == GLOBAL_OK else 0)
            if run['score'] is not None:
                score = int(run['score'])
                status = GLOBAL_PT
            if run['status'] == GLOBAL_DQ:
                score = 0
                status = GLOBAL_DQ

            runs_list.append({
                'user_id': user_id,
                'status': status,
                'time': time,
                'prob_id': prob_id,
                'score': score,
            })
        except:
            pass

    return [problems, runs_list]