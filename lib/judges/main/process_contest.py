from lib.judges.ejudge.standings_export import load_ejudge_contest
from .global_verdicts import *

def process_contest(contest, users):

    ejudge_ids = {}
    for user in users:
        ejudge_ids[user.ejudge_id] = user.id

    problems, runs_list = load_ejudge_contest(contest.ejudge_id, ejudge_ids)

    user_info = {}

    user_ids = {user.id for user in users}

    for uid in user_ids:
        user_info[uid] = []
        for _ in range(len(problems)):
            user_info[uid].append({
                'score': 0,
                'penalty': 0,
                'verdict': None,
                'time': 0,
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

            if info['verdict'] == GLOBAL_OK or (info['verdict'] == GLOBAL_PD and (status == GLOBAL_IC or status == GLOBAL_DQ)):
                continue
            if status == GLOBAL_IC or status == GLOBAL_DQ:
                info['penalty'] += 1
            info['score'] = max(info['score'], score)
            info['verdict'] = status
            info['time'] = time
        except:
            pass

    return {
        'id': contest.id,
        'date': contest.date,
        'ejudge_id': contest.ejudge_id,
        'title': contest.title,
        'problems': problems,
        'users': user_info
    }