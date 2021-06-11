import globals
import math


def RMSSD(list_of_rr_flag):
    """
        Return a list of RMSSD per scenario (of specific participant & ride), without scenario 0.
    """
    # Creating a list whose number of places is the same as the number of scenarios, and fill it in zeros.
    listRMSSD = [0] * (globals.scenario_num + 1)
    for i in range(1, len(list_of_rr_flag)):
        if len(list_of_rr_flag[i]) != 0:
            for j in range(len(list_of_rr_flag[i])-1):
                listRMSSD[i] += (list_of_rr_flag[i][j+1] - list_of_rr_flag[i][j]) ** 2  # The numerator in the rmssd formula, is listed according to the scenarios
                globals.list_count_rr_intervals_flag[i] += 1

    for i in range(1, len(listRMSSD)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            listRMSSD[i] = math.sqrt(listRMSSD[i] / (globals.list_count_rr_intervals_flag[i]))  # For each scenario performs the rmssd formula
        else:
            listRMSSD[i] = 0
    return listRMSSD[1:len(listRMSSD)]  # return RMSSD per scenario, without scenario 0


def SDNN(list_of_rr_flag):
    """
        Return a list of SDNN per scenario (of specific participant & ride), without scenario 0.
    """
    listSumSDNN = [0] * (globals.scenario_num + 1)  # list with 0
    list_AVG_SDNN = [0] * (globals.scenario_num + 1)  # list with 0
    listSDNN = [0] * (globals.scenario_num + 1)  # list with 0
    for i in range(1, len(list_of_rr_flag)):
        listSumSDNN[i] = sum(list_of_rr_flag[i])
    for i in range(1, len(list_AVG_SDNN)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            list_AVG_SDNN[i] = (listSumSDNN[i] / (globals.list_count_rr_intervals_flag[i] + 1))
        else:
            list_AVG_SDNN[i] = 0
    for i in range(1, len(list_of_rr_flag)):
        if len(list_of_rr_flag[i]) != 0:
            for j in range(len(list_of_rr_flag[i])):
                listSDNN[i] += (list_of_rr_flag[i][j] - list_AVG_SDNN[i]) ** 2
    for i in range(1, len(listSDNN)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            listSDNN[i] = math.sqrt(listSDNN[i] / globals.list_count_rr_intervals_flag[i])
        else:
            listSDNN[i] = 0
    return listSDNN[1:len(listSDNN)]


def SDSD(list_of_rr_flag):
    """
        Return a list of SDSD per scenario (of specific participant & ride), without scenario 0.
    """
    listSDSD = [0] * (globals.scenario_num + 1)  # list with 0
    listSumSDSD = [0] * (globals.scenario_num + 1)  # list with 0
    list_AVG_SDSD = [0] * (globals.scenario_num + 1)  # list with 0

    for i in range(1, len(list_of_rr_flag)):
        if len(list_of_rr_flag[i]) != 0:
            for j in range(len(list_of_rr_flag[i])-1):
                listSumSDSD[i] += abs(list_of_rr_flag[i][j+1] - list_of_rr_flag[i][j])
    for i in range(1, len(list_AVG_SDSD)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            list_AVG_SDSD[i] = (listSumSDSD[i] / globals.list_count_rr_intervals_flag[i])
        else:
            list_AVG_SDSD[i] = 0
    for i in range(1, len(list_of_rr_flag)):
        if len(list_of_rr_flag[i]) != 0:
            for j in range(len(list_of_rr_flag[i])-1):
                listSDSD[i] += (abs(list_of_rr_flag[i][j+1] - list_of_rr_flag[i][j]) - list_AVG_SDSD[i]) ** 2
    for i in range(1, len(listSDSD)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            listSDSD[i] = math.sqrt(listSDSD[i] / globals.list_count_rr_intervals_flag[i])
        else:
            listSDSD[i] = 0
    return listSDSD[1:len(listSDSD)]


def PNN50(list_of_rr_flag):
    """
        Return a list of PNN50 per scenario (of specific participant & ride), without scenario 0.
    """
    list_count_above50 = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    listPNN50 = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0

    for i in range(1, len(list_of_rr_flag)):
        if len(list_of_rr_flag[i]) != 0:
            for j in range(len(list_of_rr_flag[i])-1):
                if round(abs(list_of_rr_flag[i][j+1] - list_of_rr_flag[i][j]), 3) > 0.05:
                    list_count_above50[i] += 1

    for i in range(1, len(listPNN50)):
        if globals.list_count_rr_intervals_flag[i] != 0:
            listPNN50[i] = (list_count_above50[i] / globals.list_count_rr_intervals_flag[i]) * 100
        else:
            listPNN50[i] = 0
    return listPNN50[1:len(listPNN50)]


def Baseline_RMSSD(file_RR):
    """
        Return RMSSD baseline of specific participant & ride.
    """
    line = 0
    RMSSD_baseline_sum = 0
    while line < len(file_RR) - 1:
        RMSSD_baseline_sum = RMSSD_baseline_sum + (
                file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals']) ** 2
        line = line + 1
    RMSSD_baseline = math.sqrt(RMSSD_baseline_sum / (len(file_RR) - 1))  # checked
    return RMSSD_baseline


def Baseline_SDNN(file_RR):
    """
        Return SDNN baseline of specific participant & ride.
    """
    line = 0
    SDNN_baseline_sum = 0
    SDNN_baseline_sumRR = 0
    while line < len(file_RR):
        SDNN_baseline_sumRR = SDNN_baseline_sumRR + file_RR.at[line, 'RRIntervals']
        line = line + 1
    SDNN_baseline_avgRR = SDNN_baseline_sumRR / len(file_RR)
    line2 = 0
    while line2 < len(file_RR):
        SDNN_baseline_sum += (file_RR.at[line2, 'RRIntervals'] - SDNN_baseline_avgRR) ** 2
        line2 = line2 + 1
    SDNN_baseline = math.sqrt(SDNN_baseline_sum / (len(file_RR) - 1))
    return SDNN_baseline


def Baseline_SDSD(file_RR):
    """
        Return SDSD baseline of specific participant & ride.
    """
    line = 0
    SDSD_baseline_sum_DIFF_RR = 0
    SDSD_baseline_sum = 0
    while line < len(file_RR) - 1:
        SDSD_baseline_sum_DIFF_RR += abs(file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'])
        line = line + 1
    SDSD_baseline_avg_D = SDSD_baseline_sum_DIFF_RR / (len(file_RR) - 1)
    line2 = 0
    while line2 < len(file_RR) - 1:
        SDSD_baseline_sum += (abs(file_RR.at[line2 + 1, 'RRIntervals'] - file_RR.at[line2, 'RRIntervals']) - SDSD_baseline_avg_D) ** 2
        line2 = line2 + 1
    SDSD_baseline = math.sqrt(SDSD_baseline_sum / (len(file_RR) - 1))
    return SDSD_baseline


def Baseline_PNN50(file_RR):
    """
        Return PNN50 baseline of specific participant & ride.
    """
    line = 0
    count_D_above50ms = 0
    while line < len(file_RR) - 1:
        if round(abs(file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals']), 3) > 0.05:
            count_D_above50ms += 1
        line = line + 1
    PNN50_baseline = (count_D_above50ms / (len(file_RR) - 1)) * 100
    return PNN50_baseline
