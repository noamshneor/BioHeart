import os

import numpy as np
import pandas

import HRV_METHODS
import globals


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
    while i < len(par):  # while there are still rows to match in ECG/RR
        if j < len(parSIM):
            if parSIM.at[j - 1, 'Time'] <= par.at[i, 'Time'] < parSIM.at[j, 'Time']:
                # if time in ECG/RR between time range in SIM
                if int(parSIM.at[j - 1, 'Scenario']) != 0:
                    par.at[i, 'Scenario'] = parSIM.at[j, 'Scenario']  # match the flag
                    lst[par.at[i, 'Scenario']].append(par.at[i, col_name])

                    if col_name == "BPM":
                        dq_start_end_min_max_null(i, j, par, parSIM)
                i += 1  # move to the next ECG/RR row to match
            else:
                j += 1  # move to the next SIM start range


def dq_start_end_min_max_null(i, j, par, parSIM):
    globals.list_end_time[int(parSIM.at[j - 1, 'Scenario']) - 1] = round(parSIM.at[j - 1, 'Time'],
                                                                         4)  # insert end time - all the time till the end
    if globals.list_start_time[int(parSIM.at[j - 1, 'Scenario']) - 1] == 0:
        globals.list_start_time[int(parSIM.at[j - 1, 'Scenario']) - 1] = round(
            parSIM.at[j - 1, 'Time'], 4)  # insert start time for the specific scenario
    if par.at[i, 'BPM'] < globals.list_min_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1]:
        globals.list_min_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1] = par.at[i, 'BPM']
    if par.at[i, 'BPM'] > globals.list_max_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1]:
        globals.list_max_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1] = par.at[i, 'BPM']
    if par.at[i, 'BPM'] is None:
        globals.list_null_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1] += 1


def rr_time_match(parRR):
    """
    filling Time coloumn in RR file
    :param parRR: DataFrame of RR data
    """
    i = 1
    while i < len(parRR):
        parRR.at[i, 'Time'] = parRR.at[i - 1, 'Time'] + parRR.at[i - 1, 'RRIntervals']
        i += 1


def initial_list_of_existing_par():
    globals.list_of_existing_par = [*range(1, globals.par_num + 1)]
    for num in globals.list_of_existing_par:
        if num in globals.par_not_existing:
            globals.list_of_existing_par.remove(num)
    # print(globals.list_of_existing_par)


def filling_summary_table(avg_base, baseRR, last_k, listBPM, par, parRR, ride):
    globals.summary_table = globals.summary_table.append(
        pandas.DataFrame({'Participant': [par] * globals.scenario_num,
                          'Ride Number': [ride] * globals.scenario_num,
                          'Scenario': list(range(1, globals.scenario_num + 1)),
                          'Average BPM': listBPM, 'RMSSD': HRV_METHODS.RMSSD(parRR),
                          'SDSD': HRV_METHODS.SDSD(parRR), 'SDNN': HRV_METHODS.SDNN(parRR),
                          'PNN50': HRV_METHODS.PNN50(parRR),
                          'Baseline BPM': [avg_base] * globals.scenario_num,
                          'Baseline RMSSD': HRV_METHODS.Baseline_RMSSD(baseRR),
                          'Baseline SDNN': HRV_METHODS.Baseline_SDNN(baseRR),
                          'Baseline SDSD': HRV_METHODS.Baseline_SDSD(baseRR),
                          'Baseline PNN50': HRV_METHODS.Baseline_PNN50(baseRR)}))
    globals.summary_table.reset_index(drop=True, inplace=True)
    for k in range(last_k,
                   last_k + globals.scenario_num):  # filling substraction columns,for participant&ride
        globals.summary_table.at[k, 'Substraction BPM'] = abs(
            globals.summary_table.at[k, 'Baseline BPM'] - globals.summary_table.at[k, 'Average BPM'])
        globals.summary_table.at[k, 'Substraction RMSSD'] = abs(
            globals.summary_table.at[k, 'Baseline RMSSD'] - globals.summary_table.at[k, 'RMSSD'])
        globals.summary_table.at[k, 'Substraction SDNN'] = abs(
            globals.summary_table.at[k, 'Baseline SDNN'] - globals.summary_table.at[k, 'SDNN'])
        globals.summary_table.at[k, 'Substraction SDSD'] = abs(
            globals.summary_table.at[k, 'Baseline SDSD'] - globals.summary_table.at[k, 'SDSD'])
        globals.summary_table.at[k, 'Substraction PNN50'] = abs(
            globals.summary_table.at[k, 'Baseline PNN50'] - globals.summary_table.at[k, 'PNN50'])
    last_k = last_k + globals.scenario_num
    return last_k


def early_process_rr(index_in_folder, ride):
    parRR = pandas.read_excel(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr",
                                           os.listdir(
                                               globals.main_path + "\\" + "ride " + str(
                                                   ride) + "\\" + "rr")[
                                               index_in_folder]),
                              names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                              engine='openpyxl')
    parRR.insert(1, 'Time', [0.00 for x in range(0, (len(parRR)))],
                 True)  # insert Time column with zero
    parRR.insert(2, 'Scenario', [0 for x in range(0, (len(parRR)))],
                 True)  # insert Scenario column with zero
    return parRR


def save_pickle(baseECG, baseRR, par, parECG, parRR, parSIM, ride):
    parECG.to_pickle(
        globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg pkl" + "\pickle_parECG" + str(par))
    parSIM.to_pickle(
        globals.main_path + "\\" + "ride " + str(ride) + "\\" + "sim pkl" + "\pickle_parSIM" + str(par))
    parRR.to_pickle(
        globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr pkl" + "\pickle_parRR" + str(par))
    baseECG.to_pickle(
        globals.main_path + "\\" + "base" + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(par))
    baseRR.to_pickle(
        globals.main_path + "\\" + "base" + "\\" + "base rr pkl" + "\pickle_baseRR" + str(par))


def dq_completeness_bpm(listBPM_per_scenario):
    for i in range(globals.scenario_num):
        globals.list_completeness_bpm[i] = str(
            round(
                ((listBPM_per_scenario[i] - globals.list_null_bpm[i]) / listBPM_per_scenario[i]) * 100,
                2)) + " %"


def avg_med_bpm(list_of_bpm_flag):
    listBPM = []  # list of Average BPM by scenario
    listBPM_per_scenario = []
    for i in range(1, globals.scenario_num + 1):
        listBPM.append(sum(list_of_bpm_flag[i]) / len(list_of_bpm_flag[i]))
        listBPM_per_scenario.append(len(list_of_bpm_flag[i]))
        globals.list_median_bpm[i - 1] = np.median(list_of_bpm_flag[i])
    return listBPM, listBPM_per_scenario


def early_process_ecg_sim(index_in_folder, ride):
    globals.list_count_rmssd = [0] * (
            globals.scenario_num + 1)  # Initialize the list to zero for each scenario
    list_of_bpm_flag = [[] for i in
                        range(
                            globals.scenario_num + 1)]  # Creates a list of lists as the number of scenarios
    parECG = pandas.read_csv(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg",
                                          os.listdir(
                                              globals.main_path + "\\" + "ride " + str(
                                                  ride) + "\\" + "ecg")[
                                              index_in_folder]),
                             sep="\t", names=['mV', 'Volts', 'BPM', 'Time'], usecols=['BPM', 'Time'],
                             skiprows=11, header=None)
    parECG['Time'] = [x / 1000 for x in range(0, (len(parECG)))]  # filling a time column
    parSIM = pandas.read_csv(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "sim",
                                          os.listdir(
                                              globals.main_path + "\\" + "ride " + str(
                                                  ride) + "\\" + "sim")[
                                              index_in_folder]),
                             sep=",", skiprows=1, usecols=[0, globals.scenario_col_num - 1],
                             names=['Time', 'Scenario'])
    parECG.insert(2, 'Scenario', [0 for x in range(0, (len(parECG)))],
                  True)  # adding scenario column and filling with 0
    return list_of_bpm_flag, parECG, parSIM


def early_process_base(index_in_folder, par):
    baseECG = pandas.read_csv(os.path.join(globals.main_path + "\\" + "base" + "\\" + "base ecg",
                                           os.listdir(
                                               globals.main_path + "\\" + "base" + "\\" + "base ecg")[
                                               index_in_folder]),
                              sep="\t",
                              names=['mV', 'Volts', 'BPM'], usecols=['BPM'],
                              skiprows=11, header=None)
    avg_base = np.average(baseECG)  # avg for column BPM at baseECG
    baseRR = pandas.read_excel(os.path.join(globals.main_path + "\\" + "base" + "\\" + "base rr",
                                            os.listdir(
                                                globals.main_path + "\\" + "base" + "\\" + "base rr")[
                                                index_in_folder]),
                               names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                               engine='openpyxl')
    return avg_base, baseRR, baseECG


def initial_data_quality():
    globals.list_start_time = [0] * globals.scenario_num
    globals.list_end_time = [0] * globals.scenario_num
    globals.list_min_bpm = [1000] * globals.scenario_num
    globals.list_max_bpm = [0] * globals.scenario_num
    globals.list_null_bpm = [0] * globals.scenario_num
    globals.list_completeness_bpm = [0] * globals.scenario_num
    globals.list_median_bpm = [0] * globals.scenario_num