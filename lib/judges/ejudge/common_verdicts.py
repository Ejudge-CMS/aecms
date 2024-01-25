from lib.judges.main.global_verdicts import *

EJUDGE_OK = 'OK'  # OK
EJUDGE_PT = 'PT'  # Partial score
EJUDGE_WA = 'WA'  # Wrong answer
EJUDGE_RT = 'RT'  # Runtime error
EJUDGE_TL = 'TL'  # Time limit exceeded
EJUDGE_PE = 'PE'  # Presentation error
EJUDGE_ML = 'ML'  # Memory limit exceeded
EJUDGE_SE = 'SE'  # Security violation
EJUDGE_CE = 'CE'  # Compilation error
EJUDGE_CF = 'CF'  # Check failed
EJUDGE_AC = 'AC'  # Accepted
EJUDGE_IG = 'IG'  # Ignored
EJUDGE_PD = 'PD'  # Pending
EJUDGE_SV = 'SV'  # Style violation
EJUDGE_WT = 'WT'  # Wall time limit exceeded
EJUDGE_PR = 'PR'  # Pending review
EJUDGE_SM = 'SM'  # Summoned for defence
EJUDGE_RJ = 'RJ'  # Rejected
EJUDGE_DQ = 'DQ'  # Disqualified

EJUDGE_TO_GLOBAL = {
    EJUDGE_OK: GLOBAL_OK,
    EJUDGE_PT: GLOBAL_PT,
    EJUDGE_WA: GLOBAL_IC,
    EJUDGE_RT: GLOBAL_IC,
    EJUDGE_TL: GLOBAL_IC,
    EJUDGE_PE: GLOBAL_IC,
    EJUDGE_ML: GLOBAL_IC,
    EJUDGE_SE: GLOBAL_IC,
    EJUDGE_CE: GLOBAL_IC,
    EJUDGE_CF: GLOBAL_IC,
    EJUDGE_AC: GLOBAL_PD,
    EJUDGE_IG: GLOBAL_IC,
    EJUDGE_PD: GLOBAL_PD,
    EJUDGE_SV: GLOBAL_IC,
    EJUDGE_WT: GLOBAL_IC,
    EJUDGE_PR: GLOBAL_PD,
    EJUDGE_SM: GLOBAL_PD,
    EJUDGE_RJ: GLOBAL_IC,
    EJUDGE_DQ: GLOBAL_DQ,
}