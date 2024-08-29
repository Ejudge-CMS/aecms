from lib.judges.ejudge.standings_export import process_ejudge_contest
from .global_verdicts import *

def process_contest(contest, users):
    return process_ejudge_contest(contest, users)