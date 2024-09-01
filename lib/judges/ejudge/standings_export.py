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


def load_ejudge_contest(contest_id):
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

            prob_id = problem_index[run['prob_id']]
            score = (1 if status == OK else 0)
            if run['score'] is not None:
                score = int(run['score'])
                status = PT
            if run['status'] == DQ:
                score = 0
                status = DQ

            runs_list.append({
                'user_id': ejudge_id,
                'status': status,
                'time': time,
                'prob_id': prob_id,
                'score': score,
            })
        except:
            pass
    return [problems, runs_list]

def process_ejudge_contest(contest, users):

    ejudge_ids = {}
    for user in users:
        ejudge_ids[user.ejudge_id] = user.id

    problems, runs_list = load_ejudge_contest(contest.ejudge_id)

    user_info = {}

    user_ids = {user.id for user in users}

    for uid in user_ids:
        user_info[uid] = []
        for _ in range(len(problems)):
            user_info[uid].append({
                'score': 0,
                'penalty': 0,
                'verdict': None
            })

    for run in runs_list:
        try:
            user_id = run['user_id']

            if user_id not in ejudge_ids:
                continue

            user_id = ejudge_ids[user_id]
            status = run['status']

            time = run['time']
            if contest.duration != 0 and time > contest.duration * 60:
                continue

            prob_id = run['prob_id']
            score = run['score']

            info = user_info[user_id][prob_id]

            if status in {IC, DQ, SV}:
                info['penalty'] += 1
            if status == DQ:
                info['verdict'] = DQ
                info['score'] = 0
                continue
            if info['verdict'] == DQ:
                continue
            if info['verdict'] == OK or (info['verdict'] == PD and status != OK):
                continue
            info['score'] = max(info['score'], score)
            info['verdict'] = status
        except:
            pass

    return {
        'id': contest.id,
        'date': contest.date,
        'ejudge_id': contest.ejudge_id,
        'title': contest.name,
        'problems': problems,
        'users': user_info
    }