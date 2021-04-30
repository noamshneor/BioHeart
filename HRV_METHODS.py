import globals
import math

def RMSSD(file_RR):
    """
    return a list of RMSSD per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    # Creating a list whose number of places is the same as the number of scenarios, and fill it in zeros.
    listRMSSD = [0] * (globals.scenario_num + 1)
    # global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    # print(len(listRMSSD))
    # print(listRMSSD)
    # print(listRMSSD[int(file_RR.at[line, 'Scenario'])])
    while line < len(file_RR) - 1:  # Go over all the lines in the file_RR
        if file_RR.at[line, 'Scenario'] != 0 and file_RR.at[line + 1, 'Scenario'] != 0:  # if the scenario is not 0
            listRMSSD[int(file_RR.at[line, 'Scenario'])] += (file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[
                line, 'RRIntervals']) ** 2  # The numerator in the rmssd formula, is listed according to the scenarios
            globals.list_count_rmssd[int(file_RR.at[line, 'Scenario'])] += 1  # counting intervals (N) for all scenarios
        line = line + 1
    # print(listRMSSD)
    # print(list_count_rmssd)
    for i in range(1, len(listRMSSD)):
        listRMSSD[i] = math.sqrt(listRMSSD[i] / (globals.list_count_rmssd[i]))  # For each scenario performs the rmssd formula
    return listRMSSD[1:len(listRMSSD)]  # return RMSSD per scenario, without scenario 0


def SDNN(file_RR):
    """
    return a list of SDNN per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """

    line = 0
    listSumSDNN = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    list_AVG_SDNN = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    listSDNN = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    # global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    while line < len(file_RR):
        if file_RR.at[line, 'Scenario'] != 0:
            listSumSDNN[int(file_RR.at[line, 'Scenario'])] += file_RR.at[line, 'RRIntervals']
        line = line + 1
    # print("listSumSDNN")
    # print(listSumSDNN)  # checked
    for i in range(1, len(list_AVG_SDNN)):
        list_AVG_SDNN[i] = (listSumSDNN[i] / (globals.list_count_rmssd[i] + 1))
    # print(list_AVG_SDNN)  # checked
    line2 = 0
    while line2 < len(file_RR):
        if file_RR.at[line2, 'Scenario'] != 0:
            listSDNN[int(file_RR.at[line2, 'Scenario'])] += (file_RR.at[line2, 'RRIntervals'] - list_AVG_SDNN[
                int(file_RR.at[line2, 'Scenario'])]) ** 2
        line2 = line2 + 1
    for i in range(1, len(listSDNN)):
        listSDNN[i] = math.sqrt(listSDNN[i] / globals.list_count_rmssd[i])
    # print("listSDNN")  # checked
    # print(listSDNN)
    return listSDNN[1:len(listSDNN)]


def SDSD(file_RR):
    """ return a list of SDSD per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    listSDSD = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    listSumSDSD = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    list_AVG_SDSD = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    # global list_count_rmssd
    while line < len(file_RR) - 1:
        if file_RR.at[line, 'Scenario'] != 0 and file_RR.at[line + 1, 'Scenario'] != 0:
            listSumSDSD[int(file_RR.at[line, 'Scenario'])] += (
                    file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'])
        line = line + 1
    # print("listSumSDSD")
    # print(listSumSDSD)
    for i in range(1, len(list_AVG_SDSD)):
        list_AVG_SDSD[i] = (listSumSDSD[i] / globals.list_count_rmssd[i])
    # print(list_AVG_SDSD)
    line = 0
    while line < len(file_RR) - 1:
        if file_RR.at[line, 'Scenario'] != 0 and file_RR.at[line + 1, 'Scenario'] != 0:
            listSDSD[int(file_RR.at[line, 'Scenario'])] += (file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[
                line, 'RRIntervals'] - list_AVG_SDSD[int(file_RR.at[line, 'Scenario'])]) ** 2
        line = line + 1
    # print("list_count_rmssd")
    # print(list_count_rmssd)
    for i in range(1, len(listSDSD)):
        listSDSD[i] = math.sqrt(listSDSD[i] / globals.list_count_rmssd[i])
    # print("listSDSD")  # checked
    # print(listSDSD)
    return listSDSD[1:len(listSDSD)]


def PNN50(file_RR):
    """
    return a list of PNN50 per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    list_count_above50 = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    listPNN50 = [0] * (globals.scenario_num + 1)  # list of 8 places,with 0
    # global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.

    while line < len(file_RR) - 1:
        if file_RR.at[line, 'Scenario'] != 0 and file_RR.at[line + 1, 'Scenario'] != 0:
            if file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'] > 0.05:
                list_count_above50[int(file_RR.at[line, 'Scenario'])] += 1
        line = line + 1
    for i in range(1, len(listPNN50)):
        listPNN50[i] = (list_count_above50[i] / globals.list_count_rmssd[i]) * 100
    # print("listPNN50")
    # print(listPNN50)
    return listPNN50[1:len(listPNN50)]


def Baseline_RMSSD(file_RR):
    """
    return RMSSD baseline of specific participant & ride,

    :param file_RR: "clean" baseline RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    RMSSD_baseline_sum = 0
    while line < len(file_RR) - 1:
        RMSSD_baseline_sum = RMSSD_baseline_sum + (
                file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals']) ** 2
        line = line + 1
    RMSSD_baseline = math.sqrt(RMSSD_baseline_sum / (len(file_RR) - 1))  # checked
    # print("RMSSD_baseline")
    # print(RMSSD_baseline)
    return RMSSD_baseline


def Baseline_SDNN(file_RR):
    """
    return SDNN baseline of specific participant & ride,

    :param file_RR: "clean" baseline RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
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
    # print("SDNN_baseline")
    # print(SDNN_baseline)  # checked
    return SDNN_baseline


def Baseline_SDSD(file_RR):
    """
    return SDSD baseline of specific participant & ride,

    :param file_RR: "clean" baseline RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    SDSD_baseline_sum_DIFF_RR = 0
    SDSD_baseline_sum = 0
    while line < len(file_RR) - 1:
        SDSD_baseline_sum_DIFF_RR = SDSD_baseline_sum_DIFF_RR + (
                file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'])
        line = line + 1
    SDSD_baseline_avg_D = SDSD_baseline_sum_DIFF_RR / (len(file_RR) - 1)
    line2 = 0
    while line2 < len(file_RR):
        SDSD_baseline_sum += (file_RR.at[line2, 'RRIntervals'] - SDSD_baseline_avg_D) ** 2
        line2 = line2 + 1
    SDSD_baseline = math.sqrt(SDSD_baseline_sum / (len(file_RR) - 1))
    # print("SDSD_baseline")
    # print(SDSD_baseline)  # checked
    return SDSD_baseline


def Baseline_PNN50(file_RR):
    """
    return PNN50 baseline of specific participant & ride,

    :param file_RR: "clean" baseline RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    count_D_above50ms = 0
    while line < len(file_RR) - 1:
        if (file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals']) > 0.05:
            # בגלל הדיוק יוצאים יותר ערכים מבאקסל
            count_D_above50ms += 1
        line = line + 1
    # print(count_D_above50ms)
    PNN50_baseline = (count_D_above50ms / (len(file_RR) - 1))
    # print("PNN50_baseline")
    # print(PNN50_baseline)
    return PNN50_baseline
