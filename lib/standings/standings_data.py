from lib.judges.main.process_contest import process_contest
from courses.models import Standings


def get_standings_data(standings: Standings):
    users_data = []
    users = standings.course.users.all()

    contests_models = standings.contests
    contests_models = contests_models.order_by('-date', '-id')
    contests = []
    for contest_model in contests_models:
        contest = process_contest(contest_model, users)
        contests.append(contest)

    for user in users:
        users_data.append({
            'id': user.id,
            'name': user.name
        })
                

    return [users_data, contests]