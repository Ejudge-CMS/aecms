from lib.judges.main import process_contest
from courses.models import Standings


def get_standings_data(standings: Standings):
    group_list = standings.groups.all()

    users_data = []
    users = []
    for group in group_list:
        users.extend(group.users.all())

    contests_models = standings.contests.filter(contest_id__isnull=False)
    contests_models = contests_models.order_by('-date', '-id')
    contests = []
    for contest_model in contests_models:
        contest = process_contest(contest_model, users)
        contests.append(contest)

    for group in group_list:
        for user in group.users.all():
            users_data.append({
                'id': user.id,
                'name': user.name,
                'group': group.name,
                'group_short': group.short_name,
            })
                

    return [users_data, contests]