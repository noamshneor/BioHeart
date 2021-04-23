import collections
import math
import time
import threading
import pandas
# import biosppy
# import HeartPy
# import NeuroKit2
import numpy as np
import os
import PySimpleGUIQt as sg
#import PySimpleGUI as psg
import matplotlib.pyplot as plt
import sys
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
#matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from multiprocessing import Process



# from ui_functions import summary_table_window_layout, loading_window_layout, path_load_window_layout, \
# open_window_layout, early_summary_table, checkFolders, checkFiles, exportCSV, add_files_in_folder
# --------------------------------------------- EARLY PROCESS FUNCTIONS ---------------------------------------------
def flag_match(par, parSIM, lst, col_name):
    """ Match the scenario flag
    from:simulation data
    to:ecg data
    --> by time

    :param par: DataFrame of par data
    :param parSIM: DataFrame of SIMULATION data
    :param lst: List of value for specific flag
    :param col_name: column name
    :type par: DataFrame
    :type parSIM: DataFrame
    :type col_name: str
    """
    i = 0
    j = 1
    while i < len(par):  # while there are still rows to match in ECG
        if j < len(parSIM):
            if parSIM.at[j - 1, 'Time'] <= par.at[i, 'Time'] < parSIM.at[j, 'Time']:
                # if time in ECG between time range in SIM
                if int(parSIM.at[j - 1, scenario_col_name]) != 0:
                    par.at[i, scenario_col_name] = parSIM.at[j, scenario_col_name]  # match the flag
                    lst[par.at[i, scenario_col_name]].append(par.at[i, col_name])
                i += 1  # move to the next ECG row to match
            else:
                j += 1  # move to the next SIM start range


def rr_time_match(parRR):
    """
    filling Time coloumn in RR file
    :param parRR: DataFrame of RR data
    """
    i = 1
    while i < len(parRR):
        parRR.at[i, 'Time'] = parRR.at[i - 1, 'Time'] + parRR.at[i - 1, 'RRIntervals']
        i += 1


def RMSSD(file_RR):
    """
    return a list of RMSSD per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """

    # file_RR = pandas.read_pickle("pickle_parRR1")
    # print(file_RR)
    # file_RR.to_csv("RR_CSV", sep='\t')

    line = 0
    listRMSSD = [0] * (
            scenario_num + 1)  # Creating a list whose number of places is the same as the number of scenarios, and fill it in zeros.
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    # print(len(listRMSSD))
    # print(listRMSSD)
    # print(listRMSSD[int(file_RR.at[line, scenario_col_name])])
    while line < len(file_RR) - 1:  # Go over all the lines in the file_RR
        if file_RR.at[line, scenario_col_name] != 0 and file_RR.at[
            line + 1, scenario_col_name] != 0:  # if the scenario is not 0
            listRMSSD[int(file_RR.at[line, scenario_col_name])] += (file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[
                line, 'RRIntervals']) ** 2  # The numerator in the rmssd formula, is listed according to the scenarios
            list_count_rmssd[int(file_RR.at[line, scenario_col_name])] += 1  # counting intervals (N) for all scenarios
        line = line + 1
    # print(listRMSSD)
    # print(list_count_rmssd)
    for i in range(1, len(listRMSSD)):
        listRMSSD[i] = math.sqrt(listRMSSD[i] / (list_count_rmssd[i]))  # For each scenario performs the rmssd formula
    return listRMSSD[1:len(listRMSSD)]  # return RMSSD per scenario, without scenario 0


def SDNN(file_RR):
    """
    return a list of SDNN per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """

    line = 0
    listSumSDNN = [0] * (scenario_num + 1)  # list of 8 places,with 0
    list_AVG_SDNN = [0] * (scenario_num + 1)  # list of 8 places,with 0
    listSDNN = [0] * (scenario_num + 1)  # list of 8 places,with 0
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    while line < len(file_RR):
        if file_RR.at[line, scenario_col_name] != 0:
            listSumSDNN[int(file_RR.at[line, scenario_col_name])] += file_RR.at[line, 'RRIntervals']
        line = line + 1
    # print("listSumSDNN")
    # print(listSumSDNN)  # checked
    for i in range(1, len(list_AVG_SDNN)):
        list_AVG_SDNN[i] = (listSumSDNN[i] / (list_count_rmssd[i] + 1))
    # print(list_AVG_SDNN)  # checked
    line2 = 0
    while line2 < len(file_RR):
        if file_RR.at[line2, scenario_col_name] != 0:
            listSDNN[int(file_RR.at[line2, scenario_col_name])] += (file_RR.at[line2, 'RRIntervals'] - list_AVG_SDNN[
                int(file_RR.at[line2, scenario_col_name])]) ** 2
        line2 = line2 + 1
    for i in range(1, len(listSDNN)):
        listSDNN[i] = math.sqrt(listSDNN[i] / list_count_rmssd[i])
    # print("listSDNN")  # checked
    # print(listSDNN)
    return listSDNN[1:len(listSDNN)]


def SDSD(file_RR):
    """ return a list of SDSD per scenario (of specific participant & ride), without scenario 0

    :param file_RR: "clean" RR file (of specific participant & ride),and ready for process
    :type file_RR: DataFrame
    """
    line = 0
    listSDSD = [0] * (scenario_num + 1)  # list of 8 places,with 0
    listSumSDSD = [0] * (scenario_num + 1)  # list of 8 places,with 0
    list_AVG_SDSD = [0] * (scenario_num + 1)  # list of 8 places,with 0
    global list_count_rmssd
    while line < len(file_RR) - 1:
        if file_RR.at[line, scenario_col_name] != 0 and file_RR.at[line + 1, scenario_col_name] != 0:
            listSumSDSD[int(file_RR.at[line, scenario_col_name])] += (
                    file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'])
        line = line + 1
    # print("listSumSDSD")
    # print(listSumSDSD)
    for i in range(1, len(list_AVG_SDSD)):
        list_AVG_SDSD[i] = (listSumSDSD[i] / list_count_rmssd[i])
    # print(list_AVG_SDSD)
    line = 0
    while line < len(file_RR) - 1:
        if file_RR.at[line, scenario_col_name] != 0 and file_RR.at[line + 1, scenario_col_name] != 0:
            listSDSD[int(file_RR.at[line, scenario_col_name])] += (file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[
                line, 'RRIntervals'] - list_AVG_SDSD[int(file_RR.at[line, scenario_col_name])]) ** 2
        line = line + 1
    # print("list_count_rmssd")
    # print(list_count_rmssd)
    for i in range(1, len(listSDSD)):
        listSDSD[i] = math.sqrt(listSDSD[i] / list_count_rmssd[i])
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
    list_count_above50 = [0] * (scenario_num + 1)  # list of 8 places,with 0
    listPNN50 = [0] * (scenario_num + 1)  # list of 8 places,with 0
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.

    while line < len(file_RR) - 1:
        if file_RR.at[line, scenario_col_name] != 0 and file_RR.at[line + 1, scenario_col_name] != 0:
            if file_RR.at[line + 1, 'RRIntervals'] - file_RR.at[line, 'RRIntervals'] > 0.05:
                list_count_above50[int(file_RR.at[line, scenario_col_name])] += 1
        line = line + 1
    for i in range(1, len(listPNN50)):
        listPNN50[i] = (list_count_above50[i] / list_count_rmssd[i]) * 100
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


# --------------------------------------------- early_process ---------------------------------------------
def early_process():
    """
    A function that arranges the raw files
    (adds columns, matches the scenario column by times for all the files)
    and performs the processing of the files. The output is a summary table with the avg heart rate
     and the heart rate variance
    """
    global scenario_num
    global scenario_col_name
    global par_num
    global par_ride_num
    global current_par
    global main_path
    global percent
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    global summary_table

    current_par = 0
    percent = 0  # Displays in percentages for how many participants the final table data has been processed
    last_k = 0  # variable that helps to know how many rows in the summary table has been filled

    for par in range(1, par_num + 1):  # loop for participants
        for ride in range(1, par_ride_num + 1):  # loop for rides
            print("Start early process for ride: " + str(ride) + "for par: " + str(par))
            list_count_rmssd = [0] * (scenario_num + 1)  # Initialize the list to zero for each scenario
            list_of_bpm_flag = [[] for i in
                                range(scenario_num + 1)]  # Creates a list of lists as the number of scenarios
            parECG = pandas.read_csv(os.path.join(main_path + "\\" + str(ride) + "\\" + "ecg",
                                                  os.listdir(main_path + "\\" + str(ride) + "\\" + "ecg")[par - 1]),
                                     sep="\t", names=['mV', 'Volts', 'BPM', 'Time'], usecols=['BPM', 'Time'],
                                     skiprows=11, header=None)
            parECG['Time'] = [x / 1000 for x in range(0, (len(parECG)))]  # filling a time column
            parSIM = pandas.read_csv(os.path.join(main_path + "\\" + str(ride) + "\\" + "sim",
                                                  os.listdir(main_path + "\\" + str(ride) + "\\" + "sim")[par - 1]),
                                     sep="\t", usecols=['Time', scenario_col_name])
            parECG.insert(2, scenario_col_name, [0 for x in range(0, (len(parECG)))],
                          True)  # adding scenario column and filling with 0
            flag_match(parECG, parSIM, list_of_bpm_flag,
                       'BPM')  # filling column 'flag' in parECG, and filling list_of_bpm_flag by scenario.

            listBPM = []  # list of Average BPM by scenario
            for i in range(1, scenario_num + 1):
                listBPM.append(sum(list_of_bpm_flag[i]) / len(list_of_bpm_flag[i]))

            # convert to pickle the "clean files"
            parECG.to_pickle(main_path + "\\" + str(ride) + "\\" + "ecg pkl" + "\pickle_parECG" + str(par))
            parSIM.to_pickle(main_path + "\\" + str(ride) + "\\" + "sim pkl" + "\pickle_parSIM" + str(par))

            parRR = pandas.read_excel(os.path.join(main_path + "\\" + str(ride) + "\\" + "rr",
                                                   os.listdir(main_path + "\\" + str(ride) + "\\" + "rr")[par - 1]),
                                      names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                                      engine='openpyxl')
            parRR.insert(1, 'Time', [0.00 for x in range(0, (len(parRR)))], True)  # insert Time column with zero
            parRR.insert(2, scenario_col_name, [0 for x in range(0, (len(parRR)))],
                         True)  # insert Scenario column with zero
            rr_time_match(parRR)  # function that fill the time column in parRR
            list_of_rr_flag = [[] for i in
                               range(scenario_num + 1)]  # Creates a list of lists as the number of scenarios
            flag_match(parRR, parSIM, list_of_rr_flag,
                       'RRIntervals')  # filling column 'flag' in parRR, and filling list_of_rr_flag by scenario.
            parRR.to_pickle(main_path + "\\" + str(ride) + "\\" + "rr pkl" + "\pickle_parRR" + str(par))
            # print(parRR)
            # ------------------------------------------ BASE ---------------------------------------
            baseECG = pandas.read_csv(os.path.join(main_path + "\\" + str(ride) + "\\" + "base ecg",
                                                   os.listdir(main_path + "\\" + str(ride) + "\\" + "base ecg")[
                                                       par - 1]),
                                      sep="\t",
                                      names=['mV', 'Volts', 'BPM'], usecols=['BPM'],
                                      skiprows=11, header=None)
            avg_base = np.average(baseECG)  # avg for column BPM at baseECG
            baseECG.to_pickle(main_path + "\\" + str(ride) + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(par))
            baseRR = pandas.read_excel(os.path.join(main_path + "\\" + str(ride) + "\\" + "base rr",
                                                    os.listdir(main_path + "\\" + str(ride) + "\\" + "base rr")[
                                                        par - 1]),
                                       names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                                       engine='openpyxl')
            baseRR.to_pickle(main_path + "\\" + str(ride) + "\\" + "base rr pkl" + "\pickle_baseRR" + str(par))
            # ----------------------------------------------------------------------------------------------------------
            # filling summary table
            summary_table = summary_table.append(pandas.DataFrame({'Participant': [par] * scenario_num,
                                                                   'Ride Number': [ride] * scenario_num,
                                                                   'Scenario': list(range(1, scenario_num + 1)),
                                                                   'Average BPM': listBPM, 'RMSSD': RMSSD(parRR),
                                                                   'SDSD': SDSD(parRR), 'SDNN': SDNN(parRR),
                                                                   'PNN50': PNN50(parRR),
                                                                   'Baseline BPM': [avg_base] * scenario_num,
                                                                   'Baseline RMSSD': Baseline_RMSSD(baseRR),
                                                                   'Baseline SDNN': Baseline_SDNN(baseRR),
                                                                   'Baseline SDSD': Baseline_SDSD(baseRR),
                                                                   'Baseline PNN50': Baseline_PNN50(baseRR)}))
            summary_table.reset_index(drop=True, inplace=True)
            for k in range(last_k, last_k + scenario_num):  # filling substraction columns,for participant&ride
                summary_table.at[k, 'Substraction BPM'] = abs(
                    summary_table.at[k, 'Baseline BPM'] - summary_table.at[k, 'Average BPM'])
                summary_table.at[k, 'Substraction RMSSD'] = abs(
                    summary_table.at[k, 'Baseline RMSSD'] - summary_table.at[k, 'RMSSD'])
                summary_table.at[k, 'Substraction SDNN'] = abs(
                    summary_table.at[k, 'Baseline SDNN'] - summary_table.at[k, 'SDNN'])
                summary_table.at[k, 'Substraction SDSD'] = abs(
                    summary_table.at[k, 'Baseline SDSD'] - summary_table.at[k, 'SDSD'])
                summary_table.at[k, 'Substraction PNN50'] = abs(
                    summary_table.at[k, 'Baseline PNN50'] - summary_table.at[k, 'PNN50'])
                # print(summary_table_par.at[k, 'Substraction BPM'])
                # print("k:"+str(k))
            last_k = last_k + scenario_num
            # print("last k:"+str(last_k))
            # print(summary_table_par[['Participant', 'Ride Number', 'Substraction BPM','Substraction RMSSD','Substraction SDNN','Substraction SDSD','Substraction PNN50']])
            # summary_table_par.to_pickle("summary_table_par" + str(par))#אם היינו רוצות לשמור טבלה לכל ניבדק בנפרד
            percent += (1 / par_num) / par_ride_num
        current_par = par
        print(percent * 100)
    # print(summary_table)
    summary_table.to_pickle("summary_table")


def pickle_early_process():
    """
    A function that arranges the "clean" pickles files and performs the processing of the files.
    The output is a summary table with the avg heart rate and the heart rate variance
    """
    global scenario_num
    global scenario_col_name
    global par_num
    global par_ride_num
    global current_par
    global main_path
    global percent
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    global summary_table

    current_par = 0
    percent = 0  # Displays in percentages for how many participants the final table data has been processed
    last_k = 0  # variable that helps to know how many rows in the summary table has been filled

    for par in range(1, par_num + 1):  # loop for participants
        for ride in range(1, par_ride_num + 1):  # loop for rides
            print("Start early process for ride: " + str(ride) + "for par: " + str(par))
            list_count_rmssd = [0] * (scenario_num + 1)  # Initialize the list to zero for each scenario
            list_of_bpm_flag = [[] for i in range(scenario_num + 1)]
            parECG_pickle = pandas.read_pickle(
                main_path + "\\" + str(ride) + "\\" + "ecg pkl" + "\pickle_parECG" + str(par))
            parRR_pickle = pandas.read_pickle(
                main_path + "\\" + str(ride) + "\\" + "rr pkl" + "\pickle_parRR" + str(par))

            line = 0
            while line < len(parECG_pickle):  # while there are still rows in ECG
                list_of_bpm_flag[parECG_pickle.at[line, scenario_col_name]].append(
                    parECG_pickle.at[line, 'BPM'])  # create list of list-> BPM by scenario
                line += 1  # move to the next ECG row

            listBPM = []
            for i in range(1, scenario_num + 1):
                listBPM.append(
                    sum(list_of_bpm_flag[i]) / len(list_of_bpm_flag[i]))  # list with Average BPM for each scenario
            # print(sum(list_of_bpm_flag[i]))
            # print(len(list_of_bpm_flag[i]))

            list_of_rr_flag = [[] for i in range(scenario_num + 1)]
            line = 0
            while line < len(parRR_pickle):  # while there are still rows in RR file
                list_of_rr_flag[parRR_pickle.at[line, scenario_col_name]].append(
                    parRR_pickle.at[line, 'RRIntervals'])  # create list of list-> RR by scenario
                line += 1  # move to the next ECG row

            # ------------------------------------------ BASE ---------------------------------------
            baseECG_pickle = pandas.read_pickle(
                main_path + "\\" + str(ride) + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(par))
            avg_base = np.average(baseECG_pickle)
            baseRR_pickle = pandas.read_pickle(
                main_path + "\\" + str(ride) + "\\" + "base rr pkl" + "\pickle_baseRR" + str(par))
            # ----------------------------------------------------------------------------------------------------------
            summary_table = summary_table.append(pandas.DataFrame({'Participant': [par] * scenario_num,
                                                                   'Ride Number': [ride] * scenario_num,
                                                                   'Scenario': list(range(1, scenario_num + 1)),
                                                                   'Average BPM': listBPM, 'RMSSD': RMSSD(parRR_pickle),
                                                                   'SDSD': SDSD(parRR_pickle),
                                                                   'SDNN': SDNN(parRR_pickle),
                                                                   'PNN50': PNN50(parRR_pickle),
                                                                   'Baseline BPM': [avg_base] * scenario_num,
                                                                   'Baseline RMSSD': Baseline_RMSSD(
                                                                       baseRR_pickle) * scenario_num,
                                                                   'Baseline SDNN': Baseline_SDNN(
                                                                       baseRR_pickle) * scenario_num,
                                                                   'Baseline SDSD': Baseline_SDSD(
                                                                       baseRR_pickle) * scenario_num,
                                                                   'Baseline PNN50': Baseline_PNN50(
                                                                       baseRR_pickle) * scenario_num}))

            summary_table.reset_index(drop=True, inplace=True)
            # print(summary_table)
            for k in range(last_k, last_k + scenario_num):
                summary_table.at[k, 'Substraction BPM'] = abs(
                    summary_table.at[k, 'Baseline BPM'] - summary_table.at[k, 'Average BPM'])
                summary_table.at[k, 'Substraction RMSSD'] = abs(
                    summary_table.at[k, 'Baseline RMSSD'] - summary_table.at[k, 'RMSSD'])
                summary_table.at[k, 'Substraction SDNN'] = abs(
                    summary_table.at[k, 'Baseline SDNN'] - summary_table.at[k, 'SDNN'])
                summary_table.at[k, 'Substraction SDSD'] = abs(
                    summary_table.at[k, 'Baseline SDSD'] - summary_table.at[k, 'SDSD'])
                summary_table.at[k, 'Substraction PNN50'] = abs(
                    summary_table.at[k, 'Baseline PNN50'] - summary_table.at[k, 'PNN50'])
                # print(summary_table_par.at[k, 'Substraction BPM'])
                # print("k:"+str(k))
            last_k = last_k + scenario_num
            # print("last k:"+str(last_k))
            # print(summary_table_par[['Participant', 'Ride Number', 'Substraction BPM','Substraction RMSSD','Substraction SDNN','Substraction SDSD','Substraction PNN50']])
            # summary_table_par.to_pickle("summary_table_par" + str(par))#אם היינו רוצות לשמור טבלה לכל ניבדק בנפרד
            percent += (1 / par_num) / par_ride_num
        current_par = par
        print(percent * 100)
    # print(summary_table)
    # summary_table.to_pickle("summary_table")

    # print(summary_table_par)#checked
    # summary_table_par.to_csv('summary_table_par.csv', index=False, header=True)#checked


# --------------------------------------------- UI FUNCTIONS ---------------------------------------------
def draw_plot1(participant_num_input, ride_input, table):
    x = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Scenario']]
    print(x)
    y = table.loc[
        (table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Average BPM']]
    print(y)
    plt.plot(x, y, marker='.')
    plt.title('AVG BPM of participant ' + str(participant_num_input)+' in ride ' + str(ride_input)+', by scenario')
    plt.xlabel('Scenario')
    plt.ylabel('AVG BPM')
    plt.show()



def draw_plot2(participants_input, ride_input,table):
    for line_par in participants_input:
        x2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['Scenario']]
        y2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['RMSSD']]
        #plt.plot(x2, y2, color='k', marker='.', label='participant'+str(line_par))
        plt.plot(x2, y2, label='participant'+str(line_par))
    plt.title('RMSSD of participants ' + str(participants_input)+' in ride ' + str(ride_input)+', by scenario')
    plt.xlabel('Scenario')
    plt.ylabel('RMSSD')
    plt.legend()  # מקרא
    plt.style.use('fivethirtyeight')
    plt.show()

"""
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')

def PyplotSimple():
    import numpy as np
    import matplotlib.pyplot as plt
    t = np.arange(0., 5., 0.2)

    plt.plot(t, t, 'r--', t, t ** 2, 'bs', t, t ** 3, 'g^')

    fig = plt.gcf()  # get the figure to show
    return fig
"""
##########################################
def graphs_window_layout():
    global par_num
    global par_ride_num
    participants_list = list(range(1, par_num + 1))
    rides_list = list(range(1, par_ride_num + 1))
    layout_graphs_window = \
        [
            [sg.Text(text="", background_color="transparent", size_px=(0, 90), )],  # first row
            [  # second row
                sg.Text(text="", background_color="transparent", size_px=(550, 50), justification="center"),
                sg.Text(text="choose graph", background_color="transparent", text_color='black',
                        size_px=(600, 100), font=("Century Gothic", 42, 'bold')),
            ],
            [  # third row
                sg.Text("", background_color="transparent", size=(0, 20))
            ],
            [
                sg.Radio(group_id="GRAPH", text="   AVG BPM for specific participant", background_color="transparent",
                         key='avg bpm 1 par', size_px=(670, 35), font=("Century Gothic", 16, 'bold'), enable_events=True, text_color='red'),
                #sg.Graph(canvas_size=(400, 400), graph_bottom_left=(-105, -105), graph_top_right=(105, 105),
                        # background_color='white', key='graph', tooltip='This is a cool graph!')
                #sg.Canvas(size=(200,200), background_color='white',key='-CANVAS-')
            ],
            [
                sg.Text('        participants number:', size=(32, 1), background_color="transparent", visible=False,
                        key='participant graph1',
                        font=("Century Gothic", 12), text_color='black'),
                sg.Combo(values=participants_list, size=[50, 25], key='combo_par_graph1', visible=False,
                         enable_events=True,
                         font=("Century Gothic", 12), readonly=True, default_value=""),

            ],
            [
                sg.Text('        ride number:', size=(32, 1), background_color="transparent", visible=False,
                        key='ride graph1',
                        font=("Century Gothic", 12), text_color='black'),
                sg.Combo(values=rides_list, size=[50, 25], key='combo_ride_graph1', visible=False, enable_events=True,
                         font=("Century Gothic", 12), readonly=True, default_value=""),

            ],
            [
                sg.Text("", background_color="transparent", size=(0, 40)),
            ],
            [
                sg.Radio(group_id="GRAPH", text="  RMSSD of participants", background_color="transparent",
                         key="rmssd for several par", size=(670, 35), font=("Century Gothic", 16, 'bold'), enable_events=True,
                         text_color='red'),
            ],
            [
                sg.Text('        participants number:', size=(32, 1), background_color="transparent", visible=False,
                        key='participant graph2',
                        font=("Century Gothic", 12), text_color='black'),
                #sg.Input(size=[120, 25], key='combo_par_graph2', visible=False, enable_events=True,
                        # font=("Century Gothic", 12))
                sg.Listbox(participants_list, size=(10, 2), key='combo_par_graph2', select_mode='multiple', visible=False,enable_events=True, font=("Century Gothic", 12))

            ],
            [
                sg.Text('        ride number:', size=(32, 1), background_color="transparent", visible=False,
                        key='ride graph2', font=("Century Gothic", 12), text_color='black'),
                sg.Combo(values=rides_list, size=[50, 25], key='combo_ride_graph2', visible=False, enable_events=True,
                         font=("Century Gothic", 12), readonly=True),

            ],
            [
                sg.Text("", background_color="transparent", size=(0, 200)),
            ],
            [
                sg.Text("", background_color="transparent", size=(320, 200)),
            ],
            [
                sg.Text("", background_color="transparent", size=(630, 35),
                        font=("Century Gothic", 16)),
                sg.Button("BACK", size=(150, 45), font=("Century Gothic", 18), key="graphs back",
                          enable_events=True),
                sg.Text("", background_color="transparent", size=(80, 35),
                        font=("Century Gothic", 16)),
                sg.Button("CONTINUE", size=(220, 45), font=("Century Gothic", 18), key="CONTINUE_GRAPH",
                          enable_events=True)
            ]

        ]
    return layout_graphs_window


def summary_table_window_layout(summary_table_list):
    global summary_table
    global header
    layout_summary_table_window = \
        [
            [
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(0, 140), )],
                    [sg.Checkbox("Average BPM", background_color='transparent', key='Average BPM', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Checkbox("RMSSD", background_color='transparent', key='RMSSD', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Checkbox("SDSD", background_color='transparent', key='SDSD', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Checkbox("SDNN", background_color='transparent', key='SDNN', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Checkbox("pNN50", background_color='transparent', key='pNN50', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Checkbox("Baseline BPM", background_color='transparent', key='Baseline BPM', default=True,
                                 enable_events=True, font=("Century Gothic", 13))],
                    [sg.Text(text="", background_color="transparent", size_px=(0, 60))],
                    [sg.Button(button_text="Export to CSV", size_px=(250, 60), key="Export to CSV",
                               enable_events=True,
                               font=("Century Gothic", 16))]
                ], background_color="transparent"),
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(0, 60))],
                    [sg.Table(values=summary_table_list, headings=header,
                              auto_size_columns=True,
                              num_rows=18, background_color="white",
                              enable_events=True, key="SumTable", font=("Century Gothic", 10),
                              text_color="black", justification='center')],
                    [sg.Text(text="", background_color="transparent", size_px=(100, 100))],
                ], background_color="transparent"
                ),
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(200, 450))],
                    [sg.Button(button_text="Graphs", size_px=(150, 60), key="Graphs button", enable_events=True,
                               font=("Century Gothic", 16))],
                    [sg.Text(text="", background_color="transparent", size_px=(200, 50))],
                    [sg.Button(button_text="EXIT", size_px=(100, 60), key="summary exit", enable_events=True,
                               font=("Century Gothic", 16))],
                ], background_color="transparent", element_justification="center"
                )
            ]
        ]
    return layout_summary_table_window


def loading_window_layout():
    layout_loading_window = \
        [
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 70))
            ],
            [
                sg.Text(text="                  0 of " + str(par_num), background_color="transparent",
                        text_color='black',
                        size_px=(430, 35), font=("Century Gothic", 20), key="num of num", enable_events=True)
            ],
            [
                sg.Text(text="                  ", background_color="transparent", size_px=(196, 35)),
                sg.Text(text=str(percent * 100) + " %", background_color="transparent", text_color='black',
                        size_px=(200, 60),
                        font=("Century Gothic", 20), key="percent", enable_events=True),
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 40))
            ],
            [
                sg.Text(text="    Time elapsed:  ", background_color="transparent", text_color='black',
                        size_px=(300, 35), font=("Century Gothic", 16)),
                sg.Text("00:00:00", background_color="transparent", text_color='black', size_px=(150, 35),
                        font=("Century Gothic", 16), key="Time elapsed", enable_events=True)
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 100))
            ],
            [
                sg.Text(text="  ", background_color="transparent", size_px=(10, 50)),
                sg.ProgressBar(max_value=100, start_value=0, orientation='h', size_px=(450, 50), key="p bar", )
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 30))
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(210, 50)),
                sg.Button(button_text="CANCEL", size_px=(80, 50), key="p bar cancel", enable_events=True)
            ],

        ]
    return layout_loading_window


def path_load_window_layout():
    layout_path_load_window = \
        [
            [
                sg.Text("", background_color="transparent", size=(0, 15)),
            ],
            [
                sg.Text("", background_color="transparent", size=(1050, 20)),
                sg.Text("Please choose the main folder", background_color="transparent",
                        font=("Century Gothic", 18, 'bold'),
                        text_color='black', size=(650, 30)),
            ],
            [
                sg.Text("", background_color="transparent", size=(1100, 20)),
                sg.Radio(group_id="LOAD", text="New Load", background_color='transparent', key='NEW LOAD', default=True,
                         font=("Century Gothic", 13, 'bold'), text_color='red', size_px=(200, 30)),
                sg.Radio(group_id="LOAD", text="Existing PKL Load", background_color='transparent', key='EXIST LOAD',
                         font=("Century Gothic", 13, 'bold'), text_color='red', size_px=(300, 30)),
            ],
            [
                sg.Text("", background_color="transparent", size=(1010, 20)),
                sg.Text("Main Folder", background_color="transparent", text_color='black',
                        font=("Century Gothic", 12, 'bold'), size_px=(150, 30)),
                sg.In(size=(45, 1), enable_events=True, key="-MAIN FOLDER-", font=("Century Gothic", 9)),
                sg.FolderBrowse(button_text="...", enable_events=True, key="main path button", size=(40, 35)),
            ],
            [
                sg.Text("", background_color="transparent", size=(1160, 20)),
                sg.Tree(data=treedata,
                        headings="",
                        auto_size_columns=False,
                        num_rows=20,
                        def_col_width=0,
                        col0_width=0,
                        key='-TREE-',
                        size_px=(490, 600),
                        text_color='black',
                        background_color='white',
                        show_expanded=False,
                        enable_events=True),
            ],
            [
                sg.Text("", background_color="transparent", size=(1225, 20)),
                sg.Button("EXIT", size=(110, 45), font=("Century Gothic", 18)),
                sg.Text("", background_color="transparent", size=(50, 35),
                        font=("Century Gothic", 16)),
                sg.Button("CONTINUE", size=(220, 45), font=("Century Gothic", 18), key="CONTINUE_PATH",
                          enable_events=True),
            ],
            [
                sg.Text("", background_color="transparent", size=(0, 200)),
            ]
        ]
    return layout_path_load_window


def open_window_layout():
    layout_open_window = \
        [
            [
                sg.Text("", background_color="transparent", size=(250, 500))
            ],
            [
                sg.Text("                             Participant’s number", background_color="transparent",
                        size=(670, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[80, 40], justification="center", key="par_num", enable_events=True,
                         font=("Century Gothic", 14)),
                sg.Text("          Number of participant’s rides", background_color="transparent",
                        size=(650, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Combo(values=[1, 2, 3, 4, 5], size=[50, 40], key='par_ride_num', enable_events=True,
                         font=("Century Gothic", 16), readonly=True)

            ],
            [
                sg.Text("", background_color="transparent", size=(250, 20)),
            ],
            [
                sg.Text("                             Scenario’s number", background_color="transparent",
                        size=(670, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[80, 40], justification="center", key='scenario_num', enable_events=True,
                         font=("Century Gothic", 14)),
                sg.Text("          Scenario’s column name", background_color="transparent",
                        size=(580, 35), font=("Century Gothic", 18), text_color='black'),
                sg.InputText(size=[180, 40], justification="center", key='scenario_col_name', enable_events=True,
                             font=("Century Gothic", 14))
            ],
            [
                sg.Text("", background_color="transparent", size=(320, 300)),
            ],
            [
                sg.Text("                                   ", background_color="transparent", size=(670, 35),
                        font=("Century Gothic", 16)),
                sg.Button("EXIT", size=(110, 45), font=("Century Gothic", 18), key="EXIT_OPEN",
                          enable_events=True),
                sg.Text("", background_color="transparent", size=(80, 35),
                        font=("Century Gothic", 16)),
                sg.Button("CONTINUE", size=(220, 45), font=("Century Gothic", 18), key="CONTINUE_OPEN",
                          enable_events=True)
            ]
        ]
    return layout_open_window


def early_summary_table():
    summary_table_list = summary_table.values.tolist()
    summary_table_int = [list(map(int, x)) for x in summary_table_list]
    for i in range(len(summary_table_list)):
        summary_table_list[i][0] = summary_table_int[i][0]
        summary_table_list[i][1] = summary_table_int[i][1]
        summary_table_list[i][2] = summary_table_int[i][2]
    summary_table_list = [list(map(str, x)) for x in summary_table_list]  # make str list
    summary_table_dataframe = pandas.DataFrame(data=summary_table_list, columns=header)
    #summary_table_dataframe.to_pickle("summary_table")
    return summary_table_dataframe, summary_table_list


def checkFolders(load_list, values):
    flag = True
    message = "Missing folders:"
    for ride in range(1, par_ride_num + 1):
        for folder in range(0, len(load_list)):
            if not os.path.isdir(
                    values["-MAIN FOLDER-"] + "\\" + str(ride) + "\\" + load_list[folder]):
                flag = False
                message += " " + str(ride) + "\\" + load_list[folder] + " "
    if not flag:
        sg.popup_quick_message(message, font=("Century Gothic", 14),
                               background_color='red', location=(970, 880), auto_close_duration=5)
    return flag


def checkFiles(load_list, values):
    message = "Missing files! Each folder should have EXACTLY " + str(
        par_num) + " FILES according to the number of participants"
    for ride in range(1, par_ride_num + 1):
        for folder in range(0, len(load_list)):
            if len(os.listdir(
                    values["-MAIN FOLDER-"] + "\\" + str(ride) + "\\" + load_list[folder])) != par_num:
                sg.popup_quick_message(message, font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880), auto_close_duration=5)
                return False
    return True


def exportCSV(summary_table_dataframe, values):
    headerlist = [True, True, True, values['Average BPM'], values['RMSSD'],
                  values['SDSD'], values['SDNN'], values['pNN50'], values['Baseline BPM'],
                  values['Baseline BPM'], values['RMSSD'], values['RMSSD'], values['SDNN'], values['SDNN'],
                  values['SDSD'], values['SDSD'], values['pNN50'], values['pNN50']]
    summary_table_dataframe.to_csv('summary_table.csv', index=False, header=True,
                                   columns=headerlist)
    sg.popup_quick_message('Exported successfully!', font=("Century Gothic", 10),
                           background_color='white', text_color='black',
                           location=(120, 540))


def add_files_in_folder(parent, dirname):
    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        else:

            treedata.Insert(parent, fullname, f, values=[], icon=file_icon)


# --------------------------------------------- UI ---------------------------------------------
def ui():
    global par_num
    global scenario_num
    global scenario_col_name
    global par_ride_num
    global current_par
    global summary_table
    global main_path
    global treedata
    global header
    global fig
    global participant_num_input
    # -------------------------------------------- Windows Layout --------------------------------------------
    layout_open_window = open_window_layout()
    layout_path_load_window = path_load_window_layout()
    layout_loading_window = loading_window_layout()
    layout_graphs_window = graphs_window_layout()

    correct_open_window = False  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    correct_path_window = False  # האם כל הפרטים במסך הנתיב מולאו בצורה נכונה
    newload = True  # האם נבחרה טעינה חדשה או לא - טעינה קיימת

    # -------------------------------------------- Open Windows --------------------------------------------
    open_window = sg.Window(title="BIO Heart", layout=layout_open_window, size=(1730, 970), disable_minimize=True,
                            location=(90, 0), background_image="back1.png", element_padding=(0, 0), finalize=True)
    while True:  # Create an event loop
        event, values = open_window.read()
        if event == "EXIT_OPEN" or event == sg.WIN_CLOSED:
            # End program if user closes window or presses the EXIT button
            break  # אפשר לעצור את הלולאה והחלון ייסגר

        # הגבלת השדות לקבל אך ורק ספרות בין 0 ל9 ללא שום תווים אחרים
        if event == 'par_num' and values['par_num'] and values['par_num'][-1] not in '0123456789':
            open_window['par_num'].update(values['par_num'][:-1])
        if event == 'scenario_num' and values['scenario_num'] and values['scenario_num'][-1] not in '0123456789':
            open_window['scenario_num'].update(values['scenario_num'][:-1])

        if event == "CONTINUE_OPEN":
            # ----------------------------------------- SAVE INPUT -----------------------------------------
            if (not values['par_num']) or (not values['scenario_num']) or (
                    not values['scenario_col_name']):
                # בדיקה האם אחד מ3 השדות לפחות לא מלא
                sg.popup_quick_message('Please fill in all the fields', font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880))
            else:  # כולם מלאים
                # שמירת האינפוטים במשתנים
                par_num = int(values['par_num'])
                par_ride_num = int(values['par_ride_num'])
                scenario_num = int(values['scenario_num'])
                scenario_col_name = values['scenario_col_name']
                correct_open_window = True  # כל הפרטים במסך נכונים, אפשר להמשיך למסך הבא
                break  # אפשר לעצור את הלולאה והחלון ייסגר
    open_window.close()  # פקודת סגירת חלון ביציאה מהלולאה

    if correct_open_window:  # רק אם כל הפרטים היו נכונים ונשמרו במסך הקודם
        # כלומר - אם החלון הקודם נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
        # -------------------------------------------- Path Load Windows --------------------------------------------
        path_load_window = sg.Window(title="BIO Heart", layout=layout_path_load_window, size=(1730, 970),
                                     disable_minimize=True,
                                     location=(90, 0), background_image="back2.png", element_padding=(0, 0),
                                     finalize=True)
        while True:
            event2, values2 = path_load_window.read()
            if event2 == "EXIT" or event2 == sg.WIN_CLOSED:
                break
            if event2 == "-MAIN FOLDER-":
                '''
                treedata.tree_dict.clear()
                treedata.root_node.children.clear()
                treedata.root_node = treedata.Node("", "", 'root', [], None)
                treedata.tree_dict[""] = treedata.root_node
                print(treedata)
                '''
                if values2["-MAIN FOLDER-"]:  # רק אם הוכנס נתיב והוא לא ריק
                    treedata = sg.TreeData()
                    add_files_in_folder('', values2["-MAIN FOLDER-"])
                    path_load_window['-TREE-'].update(treedata)  # הצגת תכולת התיקייה שנבחרה

            if event2 == "CONTINUE_PATH":
                # check if can continue - להפוך לפונקציה
                if not values2["-MAIN FOLDER-"]:  # אם הנתיב ריק ולא נבחר
                    sg.popup_quick_message("Please fill in the Main Folder's field", font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880))
                else:
                    flag = True  # מסמן האם הכל תקין או שיש תיקיה חסרה
                    message = "Missing rides folders in your Main Folder:"  # תחילת ההודעה
                    for ride in range(1, par_ride_num + 1):
                        if not os.path.isdir(values2["-MAIN FOLDER-"] + "\\" + str(ride)):
                            flag = False  # יש תיקיה חסרה
                            message += " \"" + str(ride) + "\" "  # שרשור ההודעה עם שם התיקיה שחסרה
                    if not flag:  # אם יש תיקיה חסרה
                        sg.popup_quick_message(message, font=("Century Gothic", 14),
                                               background_color='red', location=(970, 880), auto_close_duration=5)
                    else:  # הכל תקין
                        if values2["NEW LOAD"]:  # אם מדובר בטעינה חדשה
                            newload = True
                            new_load_list = ["ecg", "sim", "rr", "base ecg", "base rr"]  # רשימת התיקיות לבדיקה
                            if checkFolders(new_load_list, values2):  # בדיקת תיקיות קיימות
                                if checkFiles(new_load_list,
                                              values2):  # בדיקה האם בכל תת תיקיה יש מספר קבצים כמספר הנבדקים שהוזנו כקלט
                                    correct_path_window = True  # הכל תקין אפשר להמשיך
                                    break  # אפשר לעצור את הלולאה והחלון ייסגר
                        else:  # מדובר בטעינה קיימת
                            newload = False
                            exist_load_list = ["ecg pkl", "sim pkl", "rr pkl", "base ecg pkl",
                                               "base rr pkl"]  # רשימת התיקיות לבדיקה
                            if checkFolders(exist_load_list, values2):
                                if checkFiles(exist_load_list, values2):
                                    correct_path_window = True
                                    break
        path_load_window.close()

    if correct_path_window:  # אם החלון נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
        # ------------------------------------------- LOADING Window -------------------------------------------
        loading_window = sg.Window(title="loading", layout=layout_loading_window, size=(500, 500),
                                   disable_minimize=False, no_titlebar=True, keep_on_top=True,
                                   location=(700, 250), background_image="load.png", element_padding=(0, 0),
                                   finalize=True)
        start_time = time.time()  # קביעת זמן התחלת ריצת החלון
        t = threading.Thread(
            target=early_process if newload else pickle_early_process)  # הרצת טרד במקביל על הפונקציה המתאימה שרצה ברקע של המסך
        t.setDaemon(True)  # גורם לטרד למות כשנרצה שהוא ימות
        t.start()  # התחלת ריצת הטרד

        while True:
            event3, values3 = loading_window.read(timeout=10)
            # ---------------------------------- update window elements ----------------------------------
            loading_window.element("num of num").update(
                "                  " + str(current_par) + " of " + str(par_num))
            loading_window.element("percent").update(str(round(percent * 100, 1)) + " %")

            elapsed_time = time.time() - start_time
            loading_window.element("Time elapsed").update(
                time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

            loading_window.element("p bar").update_bar(percent * 100)

            if percent * 100 == 100:###############################רק ככה הרצה של 3 משתתפים ו2 נסיעות עובדת
                break
            if event3 == "p bar cancel":
                sys.exit()  # יציאה כפויה של התכנית, הטרד מת
        loading_window.close()

    if percent * 100 == 100:  # אם החלון הקודם נסגר והעיבוד באמת הסתיים, אפשר להציג את החלון הבא
        ###############################רק ככה הרצה של 3 משתתפים ו2 נסיעות עובדת
        # ----------------------- Early Summary Table -----------------------
        summary_table_dataframe, summary_table_list = early_summary_table()  # עיבוד מקדים לטבלה
        layout_summary_table_window = summary_table_window_layout(
            summary_table_list)  # יצירת הלייאאוט עם הרשימה המעודכנת של הטבלה

        # ----------------------- Summary Table Window -----------------------
        summary_table_window = sg.Window(title="Summary Table", layout=layout_summary_table_window,
                                         size=(1730, 970), resizable=True, finalize=True,
                                         disable_minimize=True,
                                         location=(90, 0), background_image="backsum.png",
                                         element_padding=(0, 0))
        # -------------------------- Graphs Window -----------------------------
        graph_window = sg.Window(title="graphs",no_titlebar=False, layout=layout_graphs_window,
                                 size=(1730, 970), resizable=True, finalize=True,
                                 disable_minimize=True,
                                 location=(90, 0), background_image="backsum.png",
                                 element_padding=(0, 0))
        #figure_agg = None
        #fig = PyplotSimple()
        #figure_agg = draw_figure(graph_window['-CANVAS-'].TKCanvas, fig)
        #canvas = FigureCanvasTkAgg(fig)
        graph_window.hide()
        while True:
            summary_table_window.element("SumTable").update(
                values=summary_table_list)  # לבדוק אם מיותר כי הטבלה מעודכנת גם בלי זה?
            event4, values4 = summary_table_window.read()
            if event4 == "summary exit" or event4 == sg.WIN_CLOSED:
                break
            if event4 == 'Export to CSV':
                exportCSV(summary_table_dataframe, values4)
            if event4 == "Graphs button":
                summary_table_window.hide()
                graph_window.un_hide()
                choose_graph_flag = False

                while True:
                    event5, values5 = graph_window.read()
                    graph_window.bring_to_front()
                    print(event5)
                    if not values5["avg bpm 1 par"] and not values5["rmssd for several par"]:  # אם שניהם לא לחוצים
                        choose_graph_flag = False
                    else:
                        choose_graph_flag = True
                    if event5 == "avg bpm 1 par":
                        graph_window['participant graph1'].update(visible=True)
                        graph_window['combo_par_graph1'].update(visible=True)
                        graph_window['ride graph1'].update(visible=True)
                        graph_window['combo_ride_graph1'].update(visible=True)
                        graph_window['participant graph2'].update(visible=False)
                        graph_window['combo_par_graph2'].update(visible=False)
                        graph_window['ride graph2'].update(visible=False)
                        graph_window['combo_ride_graph2'].update(visible=False)

                    if event5 == "rmssd for several par":
                        graph_window['participant graph2'].update(visible=True)
                        graph_window['combo_par_graph2'].update(visible=True)
                        graph_window['ride graph2'].update(visible=True)
                        graph_window['combo_ride_graph2'].update(visible=True)
                        graph_window['participant graph1'].update(visible=False)
                        graph_window['combo_par_graph1'].update(visible=False)
                        graph_window['ride graph1'].update(visible=False)
                        graph_window['combo_ride_graph1'].update(visible=False)

                    if event5 == "graphs back":
                        # End program if user closes window or presses the EXIT button
                        # summary_table_window.un_hide()
                        graph_window.hide()
                        summary_table_window.un_hide()
                        graph_window['participant graph1'].update(visible=False)
                        graph_window['combo_par_graph1'].update(visible=False)
                        graph_window['ride graph1'].update(visible=False)
                        graph_window['combo_ride_graph1'].update(visible=False)
                        graph_window['participant graph2'].update(visible=False)
                        graph_window['combo_par_graph2'].update(visible=False)
                        graph_window['ride graph2'].update(visible=False)
                        graph_window['combo_ride_graph3'].update(visible=False)
                        choose_graph_flag = False
                        break

                    if event5 == "CONTINUE_GRAPH":
                        if values5["avg bpm 1 par"] and choose_graph_flag:
                            # שמירת האינפוטים במשתנים
                            participant_num_input = int(values5['combo_par_graph1'])
                            ride_input = int(values5['combo_ride_graph1'])
                            p1 = Process(target=draw_plot1, args=(participant_num_input, ride_input, table))
                            p1.start()
                            choose_graph_flag = False

                        elif values5["rmssd for several par"] and choose_graph_flag:
                            # לבדוק האם הנבדקים שנכתבו תואמים לקלט במסך הפתיחה
                            participants_input = values5['combo_par_graph2']
                            ride_input = int(values5['combo_ride_graph2'])
                            p2 = Process(target=draw_plot2, args=(participants_input, ride_input, table))
                            p2.start()
                            choose_graph_flag = False

                        else:
                            sg.popup_quick_message('Please choose graph before continue',
                                                   font=("Century Gothic", 14), background_color='red',
                                                   location=(970, 880))
        graph_window.close()
        summary_table_window.close()


if __name__ == '__main__':
    # ---------------------------------------------- INPUT ----------------------------------------------
    scenario_num = 7
    scenario_col_name = "Flag"
    par_num = 1
    par_ride_num = 1
    current_par = 0
    # path_noam = r"C:\Users\user\PycharmProjects\ProjectGmar\main folder"
    main_path = r"C:\Users\sapir\Desktop\project_gmar_path"
    treedata = sg.TreeData()
    header = ["Participant", "Ride Number", "Scenario", "Average BPM", "RMSSD", "SDSD", "SDNN", "PNN50", "Baseline BPM",
              "Substraction BPM", "Baseline RMSSD", "Substraction RMSSD", "Baseline SDNN", "Substraction SDNN",
              "Baseline SDSD", "Substraction SDSD", "Baseline PNN50",
              "Substraction PNN50"]
    summary_table = pandas.DataFrame(columns=header)  # create empty table,only with columns names
    # summary_table = pandas.read_pickle("summary_table")
    # print(summary_table.values.tolist())
    # summary_table.to_csv()
    # print(summary_table)
    list_count_rmssd = []
    percent = 0

    # ------------------------------------------------ UI ------------------------------------------------

    # early_process()

    # ---------------------------------------------- graphs ----------------------------------------------
    # participant_num_input = 1# for graph1
    # ride_input = 1
    # participants_input = [1, 2, 3]# for graph2
    # -------------------graph 1-נבדק מסויים בנסיעה מסויימת בכל התרחישים שלו וקצב הלב הממוצע-------------------
    # table = pandas.read_pickle("summary_table")
    table = pandas.read_csv("summary_table_3par.csv")
    print(table)
    ui()
    """
    #--------------------graph quickly------------------------------
    choose_graph_flag = False
    layout_graphs_window = graphs_window_layout()
    graph_window = sg.Window(title="graphs", layout=layout_graphs_window,
                             size=(1730, 970), no_titlebar=False, resizable=True, finalize=True,
                             disable_minimize=True,
                             location=(90, 0), background_image="backsum.png",
                             element_padding=(0, 0))
    while True:
        event5, values5 = graph_window.read()
        graph_window.bring_to_front()
        print(event5)
        if not values5["avg bpm 1 par"] and not values5["rmssd for several par"]:#אם שניהם לא לחוצים
            choose_graph_flag = False
        else:
            choose_graph_flag = True
        if event5 == "avg bpm 1 par":
            graph_window['participant graph1'].update(visible=True)
            graph_window['combo_par_graph1'].update(visible=True)
            graph_window['ride graph1'].update(visible=True)
            graph_window['combo_ride_graph1'].update(visible=True)
            graph_window['participant graph2'].update(visible=False)
            graph_window['combo_par_graph2'].update(visible=False)
            graph_window['ride graph2'].update(visible=False)
            graph_window['combo_ride_graph2'].update(visible=False)


        if event5 == "rmssd for several par":
            graph_window['participant graph2'].update(visible=True)
            graph_window['combo_par_graph2'].update(visible=True)
            graph_window['ride graph2'].update(visible=True)
            graph_window['combo_ride_graph2'].update(visible=True)
            graph_window['participant graph1'].update(visible=False)
            graph_window['combo_par_graph1'].update(visible=False)
            graph_window['ride graph1'].update(visible=False)
            graph_window['combo_ride_graph1'].update(visible=False)

        if event5 == "graphs back":
            # End program if user closes window or presses the EXIT button
            # summary_table_window.un_hide()
            graph_window.hide()
            graph_window['participant graph1'].update(visible=False)
            graph_window['combo_par_graph1'].update(visible=False)
            graph_window['ride graph1'].update(visible=False)
            graph_window['combo_ride_graph1'].update(visible=False)
            graph_window['participant graph2'].update(visible=False)
            graph_window['combo_par_graph2'].update(visible=False)
            graph_window['ride graph2'].update(visible=False)
            graph_window['combo_ride_graph2'].update(visible=False)
            choose_graph_flag = False
            break

        if event5 == "CONTINUE_GRAPH":
            if values5["avg bpm 1 par"] and choose_graph_flag:
                # שמירת האינפוטים במשתנים
                participant_num_input = int(values5['combo_par_graph1'])
                ride_input = int(values5['combo_ride_graph1'])
                p1 = Process(target=draw_plot1, args=(participant_num_input, ride_input, table))
                p1.start()
                choose_graph_flag = False

            elif values5["rmssd for several par"] and choose_graph_flag:
                # לבדוק האם הנבדקים שנכתבו תואמים לקלט במסך הפתיחה
                participants_input = values5['combo_par_graph2']
                ride_input = int(values5['combo_ride_graph2'])
                p2 = Process(target=draw_plot2, args=(participants_input, ride_input, table))
                p2.start()
                choose_graph_flag = False

            else:
                sg.popup_quick_message('Please choose graph before continue', font=("Century Gothic", 14), background_color='red', location=(970, 880))
    graph_window.close()
    
    print(table['Average BPM'])
    print(table['Scenario'])
    print(type(table))
    x = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Scenario']]
    print(x)
    y = table.loc[
        (table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Average BPM']]
    print(y)
    plt.plot(x, y, marker='.')
    plt.title('Participant' + str(participant_num_input) + ' in Ride ' + str(ride_input) + ' AVG BPM by Scenario')
    plt.xlabel('Scenario')
    plt.ylabel('AVG BPM')
    plt.show()

    # x = table['Scenario'].tolist()#לקחת עמודה מהטבלה,כשחשבנו לעשות טבלאות נפרדות לכל נבדק
    # y = table['AVG BPM'].tolist()#לקחת עמודה מהטבלה,כשחשבנו לעשות טבלאות נפרדות לכל נבדק
    # fig = plt.gcf()# הוספתייי
    # -------------------graph 2-מספר נבדקים בנסיעה מסויימת ואת כל השונות קצב לב בכל התרחישים -------------------

    ride_input = 2
    participants_input = [1, 2]
    for line_par in participants_input:
        x2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['Scenario']]
        y2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['RMSSD']]
        #plt.plot(x2, y2, color='k', marker='.', label='participant'+str(line_par))
        plt.plot(x2, y2, label='participant'+str(line_par))

    # לראות אם יוצאים 2 גרפים שונים באותו תרשים
    table = {'First Name': ['John', 'Mary', 'Jennifer', 'Yafa'], 'Last Name': [1, 1, 2, 2], 'Age': [39, 25, 28, 30]}
    bla = pandas.DataFrame(table, columns=['First Name', 'Last Name', 'Age'])
    participants_input = [1, 2]
    for line_par in participants_input:
        x2 = bla.loc[(bla['Last Name'] == line_par), ['Age']]
        y2 = bla.loc[(bla['Last Name'] == line_par), ['Last Name']]
        # plt.plot(x2, y2, color='k', marker='.', label='participant'+str(line_par))
        plt.plot(x2, y2, label='participant' + str(line_par))
    # print(y2)

    plt.title('RMSSD of participants in ride 2, by scenario')
    plt.xlabel('Scenario')
    plt.ylabel('RMSSD')
    plt.legend()  # מקרא
    plt.style.use('fivethirtyeight')
    plt.show()

# plt.style.use('fivethirtyeight')
# plt.savefig('plot.png')

# ----------------------------------------------------------------------------------------------

    parECG_pickle = pandas.read_pickle(main_path + "\\" + str(1) + "\\" + "ecg pkl" + "\pickle_parECG" + str(1))
    parSIM_pickle = pandas.read_pickle(main_path + "\\" + str(1) + "\\" + "sim pkl" + "\pickle_parSIM" + str(1))
    print(parECG_pickle)
    print(parSIM_pickle)
    list_of_bpm_flag = [[] for i in range(scenario_num + 1)]
    print(list_of_bpm_flag)
    parRR_pickle = pandas.read_pickle(main_path + "\\" + str(1) + "\\" + "rr pkl" + "\pickle_parRR" + str(1))
    print(parRR_pickle)
    baseECG_pickle = pandas.read_pickle(main_path + "\\" + str(1) + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(1))
    print(baseECG_pickle)
"""

