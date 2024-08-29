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
    EJUDGE_OK: OK,
    EJUDGE_PT: PT,
    EJUDGE_WA: IC,
    EJUDGE_RT: IC,
    EJUDGE_TL: IC,
    EJUDGE_PE: IC,
    EJUDGE_ML: IC,
    EJUDGE_SE: IC,
    EJUDGE_CE: IC,
    EJUDGE_CF: IC,
    EJUDGE_AC: PD,
    EJUDGE_IG: IC,
    EJUDGE_PD: PD,
    EJUDGE_SV: SV,
    EJUDGE_WT: IC,
    EJUDGE_PR: PD,
    EJUDGE_SM: SM,
    EJUDGE_RJ: IC,
    EJUDGE_DQ: DQ,
}