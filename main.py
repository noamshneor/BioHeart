import time
import threading
import pandas
# import biosppy
# import HeartPy
# import NeuroKit2
import numpy as np
import os
import PySimpleGUIQt as sg
import sys
from multiprocessing import Process
import HRV_METHODS
import globals
from LAYOUT_UI import graphs_window_layout, data_quality_table_window_layout, summary_table_window_layout, \
    loading_window_layout, path_load_window_layout, open_window_layout
from UI_FUNCTIONS import draw_plot1, draw_plot2, early_summary_table, checkFolders_of_rides, checkFolders_of_base, \
    checkFiles_of_rides, checkFiles_of_base, exportCSV, add_files_in_folder


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
    while i < len(par):  # while there are still rows to match in ECG/RR
        if j < len(parSIM):
            if parSIM.at[j - 1, 'Time'] <= par.at[i, 'Time'] < parSIM.at[j, 'Time']:
                # if time in ECG/RR between time range in SIM
                if int(parSIM.at[j - 1, 'Scenario']) != 0:
                    par.at[i, 'Scenario'] = parSIM.at[j, 'Scenario']  # match the flag
                    lst[par.at[i, 'Scenario']].append(par.at[i, col_name])

                    if col_name == "BPM":
                        globals.list_end_time[int(parSIM.at[j - 1, 'Scenario'])-1] = parSIM.at[j - 1, 'Time']  # insert end time - all the time till the end
                        if par.at[i, 'BPM'] < globals.list_min_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1]:
                            globals.list_min_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1] = par.at[i, 'BPM']
                        if par.at[i, 'BPM'] > globals.list_max_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1]:
                            globals.list_max_bpm[int(parSIM.at[j - 1, 'Scenario']) - 1] = par.at[i, 'BPM']
                        if globals.list_start_time[int(parSIM.at[j - 1, 'Scenario']) - 1] == 0:
                            globals.list_start_time[int(parSIM.at[j - 1, 'Scenario']) - 1] = parSIM.at[
                                j - 1, 'Time']  # insert start time for the specific scenario
                i += 1  # move to the next ECG/RR row to match
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


# --------------------------------------------- early_process ---------------------------------------------
def early_process():
    """
    A function that arranges the raw files
    (adds columns, matches the scenario column by times for all the files)
    and performs the processing of the files. The output is a summary table with the avg heart rate
     and the heart rate variance

    global scenario_num
    global scenario_col_num
    global par_num
    global par_ride_num
    global current_par
    global main_path
    global percent
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    global summary_table
 """
    globals.current_par = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed
    last_k = 0  # variable that helps to know how many rows in the summary table has been filled

    for par in range(1, globals.par_num + 1):  # loop for participants
        for ride in range(1, globals.par_ride_num + 1):  # loop for rides
            print("Start early process for ride: " + str(ride) + " for par: " + str(par))
            globals.list_count_rmssd = [0] * (globals.scenario_num + 1)  # Initialize the list to zero for each scenario
            list_of_bpm_flag = [[] for i in
                                range(globals.scenario_num + 1)]  # Creates a list of lists as the number of scenarios
            parECG = pandas.read_csv(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg",
                                                  os.listdir(
                                                      globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg")[
                                                      par - 1]),
                                     sep="\t", names=['mV', 'Volts', 'BPM', 'Time'], usecols=['BPM', 'Time'],
                                     skiprows=11, header=None)
            parECG['Time'] = [x / 1000 for x in range(0, (len(parECG)))]  # filling a time column
            parSIM = pandas.read_csv(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "sim",
                                                  os.listdir(
                                                      globals.main_path + "\\" + "ride " + str(ride) + "\\" + "sim")[
                                                      par - 1]),
                                     sep=",", skiprows=1, usecols=[0, globals.scenario_col_num - 1],
                                     names=['Time', 'Scenario'])
            parECG.insert(2, 'Scenario', [0 for x in range(0, (len(parECG)))],
                          True)  # adding scenario column and filling with 0
            globals.list_start_time = [0] * globals.scenario_num
            globals.list_end_time = [0] * globals.scenario_num
            globals.list_min_bpm = [1000000] * globals.scenario_num
            globals.list_max_bpm = [0] * globals.scenario_num
            flag_match(parECG, parSIM, list_of_bpm_flag,
                       'BPM')  # filling column 'flag' in parECG, and filling list_of_bpm_flag by scenario.

            listBPM = []  # list of Average BPM by scenario
            listBPM_per_scenario = []
            for i in range(1, globals.scenario_num + 1):
                listBPM.append(sum(list_of_bpm_flag[i]) / len(list_of_bpm_flag[i]))
                listBPM_per_scenario.append(len(list_of_bpm_flag[i]))

            # convert to pickle the "clean files"
            parECG.to_pickle(
                globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg pkl" + "\pickle_parECG" + str(par))
            parSIM.to_pickle(
                globals.main_path + "\\" + "ride " + str(ride) + "\\" + "sim pkl" + "\pickle_parSIM" + str(par))

            parRR = pandas.read_excel(os.path.join(globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr",
                                                   os.listdir(
                                                       globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr")[
                                                       par - 1]),
                                      names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                                      engine='openpyxl')
            parRR.insert(1, 'Time', [0.00 for x in range(0, (len(parRR)))], True)  # insert Time column with zero
            parRR.insert(2, 'Scenario', [0 for x in range(0, (len(parRR)))],
                         True)  # insert Scenario column with zero
            rr_time_match(parRR)  # function that fill the time column in parRR
            list_of_rr_flag = [[] for i in
                               range(globals.scenario_num + 1)]  # Creates a list of lists as the number of scenarios
            flag_match(parRR, parSIM, list_of_rr_flag,
                       'RRIntervals')  # filling column 'flag' in parRR, and filling list_of_rr_flag by scenario.
            parRR.to_pickle(
                globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr pkl" + "\pickle_parRR" + str(par))
            # print(parRR)
            # ------------------------------------------ BASE ---------------------------------------
            baseECG = pandas.read_csv(os.path.join(globals.main_path + "\\" + "base" + "\\" + "base ecg",
                                                   os.listdir(globals.main_path + "\\" + "base" + "\\" + "base ecg")[
                                                       par - 1]),
                                      sep="\t",
                                      names=['mV', 'Volts', 'BPM'], usecols=['BPM'],
                                      skiprows=11, header=None)
            avg_base = np.average(baseECG)  # avg for column BPM at baseECG
            baseECG.to_pickle(globals.main_path + "\\" + "base" + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(par))
            baseRR = pandas.read_excel(os.path.join(globals.main_path + "\\" + "base" + "\\" + "base rr",
                                                    os.listdir(globals.main_path + "\\" + "base" + "\\" + "base rr")[
                                                        par - 1]),
                                       names=['RRIntervals'], skiprows=4, skipfooter=8, header=None,
                                       engine='openpyxl')
            baseRR.to_pickle(globals.main_path + "\\" + "base" + "\\" + "base rr pkl" + "\pickle_baseRR" + str(par))
            # ----------------------------------------------------------------------------------------------------------
            # filling summary table
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
            for k in range(last_k, last_k + globals.scenario_num):  # filling substraction columns,for participant&ride
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
                # print(summary_table_par.at[k, 'Substraction BPM'])
                # print("k:"+str(k))
            last_k = last_k + globals.scenario_num
            # print("last k:"+str(last_k))
            # print(summary_table_par[['Participant', 'Ride Number', 'Substraction BPM','Substraction RMSSD','Substraction SDNN','Substraction SDSD','Substraction PNN50']])
            # summary_table_par.to_pickle("summary_table_par" + str(par))#אם היינו רוצות לשמור טבלה לכל ניבדק בנפרד

            '''
            # filling data quality table
            data_quality_table = \
                data_quality_table.append(pandas.DataFrame({'Participant': [par] * scenario_num,
                                                            'Ride Number': [ride] * scenario_num,
                                                            'Scenario': list(range(1, scenario_num + 1)),
                                                            "Start time": globals.list_start_time,
                                                            "End time": globals.list_end_time,
                                                            "BPM(ecg) : Total number of rows": listBPM_per_scenario,
                                                            "BPM(ecg) : Number of empty rows": par,
                                                            "BPM(ecg) : % Completeness": par,
                                                            "BPM(ecg) : Minimum value": globals.list_min_bpm,
                                                            "BPM(ecg) : Maximum value": globals.list_max_bpm,
                                                            "BPM(ecg) : Median": par,
                                                            "HRV methods(rr) : Total number of rows": par,
                                                            "HRV methods(rr) : Number of empty rows": par,
                                                            "HRV methods(rr) : % Completeness": par,
                                                            "HRV methods(rr) : Minimum value": par,
                                                            "HRV methods(rr) : Maximum value": par,
                                                            "HRV methods(rr) : Median": par}))
            summary_table.reset_index(drop=True, inplace=True)
            '''
            globals.percent += (1 / globals.par_num) / globals.par_ride_num
        globals.current_par = par
        print(globals.percent * 100)
        print(globals.list_start_time)
        print(globals.list_end_time)
        print(globals.list_min_bpm)
        print(globals.list_max_bpm)
    # print(summary_table)
    # summary_table.to_pickle("summary_table") # שמרתי בפיקל בפונקציה שמכינה את הטבלה המסכמת


def pickle_early_process():
    """
    A function that arranges the "clean" pickles files and performs the processing of the files.
    The output is a summary table with the avg heart rate and the heart rate variance
    """
    globals.current_par = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed
    last_k = 0  # variable that helps to know how many rows in the summary table has been filled

    for par in range(1, globals.par_num + 1):  # loop for participants
        for ride in range(1, globals.par_ride_num + 1):  # loop for rides
            print("Start early process for ride: " + str(ride) + " for par: " + str(par))
            list_count_rmssd = [0] * (globals.scenario_num + 1)  # Initialize the list to zero for each scenario
            list_of_bpm_flag = [[] for i in
                                range(globals.scenario_num + 1)]  # רשימה של רשימות של כל ערכי הBPM לתרחיש מסוים
            parECG_pickle = pandas.read_pickle(
                globals.main_path + "\\" + "ride " + str(ride) + "\\" + "ecg pkl" + "\pickle_parECG" + str(par))
            parRR_pickle = pandas.read_pickle(
                globals.main_path + "\\" + "ride " + str(ride) + "\\" + "rr pkl" + "\pickle_parRR" + str(par))

            line = 0
            while line < len(parECG_pickle):  # while there are still rows in ECG
                list_of_bpm_flag[parECG_pickle.at[line, 'Scenario']].append(
                    parECG_pickle.at[line, 'BPM'])  # create list of list-> BPM by scenario
                line += 1  # move to the next ECG row

            listBPM = []
            for i in range(1, globals.scenario_num + 1):
                listBPM.append(
                    sum(list_of_bpm_flag[i]) / len(list_of_bpm_flag[i]))  # list with Average BPM for each scenario
            # print(sum(list_of_bpm_flag[i]))
            # print(len(list_of_bpm_flag[i]))

            list_of_rr_flag = [[] for i in range(globals.scenario_num + 1)]
            line = 0
            while line < len(parRR_pickle):  # while there are still rows in RR file
                list_of_rr_flag[parRR_pickle.at[line, 'Scenario']].append(
                    parRR_pickle.at[line, 'RRIntervals'])  # create list of list-> RR by scenario
                line += 1  # move to the next ECG row

            # ------------------------------------------ BASE ---------------------------------------
            baseECG_pickle = pandas.read_pickle(
                globals.main_path + "\\" + "base" + "\\" + "base ecg pkl" + "\pickle_baseECG" + str(par))
            avg_base = np.average(baseECG_pickle)
            baseRR_pickle = pandas.read_pickle(
                globals.main_path + "\\" + "base" + "\\" + "base rr pkl" + "\pickle_baseRR" + str(par))
            # ----------------------------------------------------------------------------------------------------------
            globals.summary_table = globals.summary_table.append(
                pandas.DataFrame({'Participant': [par] * globals.scenario_num,
                                  'Ride Number': [ride] * globals.scenario_num,
                                  'Scenario': list(range(1, globals.scenario_num + 1)),
                                  'Average BPM': listBPM, 'RMSSD': HRV_METHODS.RMSSD(parRR_pickle),
                                  'SDSD': HRV_METHODS.SDSD(parRR_pickle),
                                  'SDNN': HRV_METHODS.SDNN(parRR_pickle),
                                  'PNN50': HRV_METHODS.PNN50(parRR_pickle),
                                  'Baseline BPM': [avg_base] * globals.scenario_num,
                                  'Baseline RMSSD': HRV_METHODS.Baseline_RMSSD(
                                      baseRR_pickle) * globals.scenario_num,
                                  'Baseline SDNN': HRV_METHODS.Baseline_SDNN(
                                      baseRR_pickle) * globals.scenario_num,
                                  'Baseline SDSD': HRV_METHODS.Baseline_SDSD(
                                      baseRR_pickle) * globals.scenario_num,
                                  'Baseline PNN50': HRV_METHODS.Baseline_PNN50(
                                      baseRR_pickle) * globals.scenario_num}))

            globals.summary_table.reset_index(drop=True, inplace=True)
            # print(globals.summary_table)
            for k in range(last_k, last_k + globals.scenario_num):
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
                # print(globals.summary_table_par.at[k, 'Substraction BPM'])
                # print("k:"+str(k))
            last_k = last_k + globals.scenario_num
            # print("last k:"+str(last_k))
            # print(summary_table_par[['Participant', 'Ride Number', 'Substraction BPM','Substraction RMSSD','Substraction SDNN','Substraction SDSD','Substraction PNN50']])
            # summary_table_par.to_pickle("summary_table_par" + str(par))#אם היינו רוצות לשמור טבלה לכל ניבדק בנפרד
            globals.percent += (1 / globals.par_num) / globals.par_ride_num
        globals.current_par = par
        print(globals.percent * 100)
    # print(summary_table)
    # summary_table.to_pickle("summary_table") # שמרתי בפיקל בפונקציה שמכינה את הטבלה המסכמת

    # print(summary_table_par)#checked
    # summary_table_par.to_csv('summary_table_par.csv', index=False, header=True)#checked


# --------------------------------------------- UI ---------------------------------------------
def ui():
    # -------------------------------------------- Windows Layout --------------------------------------------
    layout_open_window = open_window_layout()
    layout_path_load_window = path_load_window_layout()
    layout_loading_window = loading_window_layout()

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
        if event == 'scenario_col_num' and values['scenario_col_num'] and values['scenario_col_num'][
            -1] not in '0123456789':
            open_window['scenario_col_num'].update(values['scenario_col_num'][:-1])

        if event == "CONTINUE_OPEN":
            # ----------------------------------------- SAVE INPUT -----------------------------------------
            if (not values['par_num']) or (not values['scenario_num']) or (
                    not values['scenario_col_num']):
                # בדיקה האם אחד מ3 השדות לפחות לא מלא
                sg.popup_quick_message('Please fill in all the fields', font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880))
            else:  # כולם מלאים
                # שמירת האינפוטים במשתנים
                globals.par_num = int(values['par_num'])
                globals.par_ride_num = int(values['par_ride_num'])
                globals.scenario_num = int(values['scenario_num'])
                globals.scenario_col_num = int(values['scenario_col_num'])
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
                    globals.treedata = sg.TreeData()
                    add_files_in_folder('', values2["-MAIN FOLDER-"])
                    path_load_window['-TREE-'].update(globals.treedata)  # הצגת תכולת התיקייה שנבחרה

            if event2 == "CONTINUE_PATH":
                # check if can continue - להפוך לפונקציה
                if not values2["-MAIN FOLDER-"]:  # אם הנתיב ריק ולא נבחר
                    sg.popup_quick_message("Please fill in the Main Folder's field", font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880))
                else:
                    flag = True  # מסמן האם הכל תקין או שיש תיקיה חסרה
                    message = "Missing rides folders in your Main Folder:"  # תחילת ההודעה
                    for ride in range(1, globals.par_ride_num + 1):
                        if not os.path.isdir(
                                values2["-MAIN FOLDER-"] + "\\" + "ride " + str(ride)) or not os.path.isdir(
                            values2["-MAIN FOLDER-"] + "\\" + "base"):
                            flag = False  # יש תיקיה חסרה
                            if not os.path.isdir(values2["-MAIN FOLDER-"] + "\\" + "ride " + str(ride)):
                                message += " \"" + "ride " + str(ride) + "\" "  # שרשור ההודעה עם שם התיקיה שחסרה
                            if not os.path.isdir(values2["-MAIN FOLDER-"] + "\\" + "base"):
                                message += " \"" + "base" + "\" "  # שרשור ההודעה עם שם התיקיה שחסרה
                    if not flag:  # אם יש תיקיה חסרה
                        sg.popup_quick_message(message, font=("Century Gothic", 14),
                                               background_color='red', location=(970, 880), auto_close_duration=5)
                    else:  # הכל תקין, אין תיקיה חסרה
                        if values2["NEW LOAD"]:  # אם מדובר בטעינה חדשה
                            newload = True
                            new_load_list_in_ride = ["ecg", "sim", "rr"]  # רשימת התיקיות לבדיקה
                            new_load_list_in_base = ["base ecg", "base rr"]  # רשימת התיקיות לבדיקה
                            if checkFolders_of_rides(new_load_list_in_ride, values2) and checkFolders_of_base(
                                    new_load_list_in_base, values2):  # בדיקת תיקיות קיימות
                                if checkFiles_of_rides(new_load_list_in_ride, values2) and checkFiles_of_base(
                                        new_load_list_in_base,
                                        values2):  # בדיקה האם בכל תת תיקיה יש מספר קבצים כמספר הנבדקים שהוזנו כקלט
                                    correct_path_window = True  # הכל תקין אפשר להמשיך
                                    globals.main_path = values2["-MAIN FOLDER-"]
                                    break  # אפשר לעצור את הלולאה והחלון ייסגר
                        else:  # מדובר בטעינה קיימת
                            newload = False
                            exist_load_list_in_ride = ["ecg pkl", "sim pkl", "rr pkl"]  # רשימת התיקיות לבדיקה
                            exist_load_list_in_base = ["base ecg pkl", "base rr pkl"]  # רשימת התיקיות לבדיקה
                            if checkFolders_of_rides(exist_load_list_in_ride, values2) and checkFolders_of_base(
                                    exist_load_list_in_base, values2):
                                if checkFiles_of_rides(exist_load_list_in_ride, values2) and checkFiles_of_base(
                                        exist_load_list_in_base, values2):
                                    correct_path_window = True  # הכל תקין אפשר להמשיך
                                    globals.main_path = values2["-MAIN FOLDER-"]
                                    break
        path_load_window.close()

    if correct_path_window:  # אם החלון נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
        # ------------------------------------------- LOADING Window -------------------------------------------
        loading_window = sg.Window(title="loading", layout=layout_loading_window, size=(500, 500),
                                   disable_minimize=True,
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
                "                  " + str(globals.current_par) + " of " + str(globals.par_num))
            loading_window.element("percent").update(str(round(globals.percent * 100, 1)) + " %")

            elapsed_time = time.time() - start_time
            loading_window.element("Time elapsed").update(
                time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

            loading_window.element("p bar").update_bar(globals.percent * 100)

            if globals.percent * 100 >= 99.99:  ###############################רק ככה הרצה של 3 משתתפים ו2 נסיעות עובדת
                break
            if event3 == "p bar cancel" or event3 == sg.WIN_CLOSED:
                sys.exit()  # יציאה כפויה של התכנית, הטרד מת
        loading_window.close()

    if globals.percent * 100 >= 99.99:  # אם החלון הקודם נסגר והעיבוד באמת הסתיים, אפשר להציג את החלון הבא
        ###############################רק ככה הרצה של 3 משתתפים ו2 נסיעות עובדת
        # ----------------------- Early Summary Table -----------------------
        summary_table_list = early_summary_table()  # עיבוד מקדים לטבלה
        layout_summary_table_window = summary_table_window_layout(
            summary_table_list)  # יצירת הלייאאוט עם הרשימה המעודכנת של הטבלה
        # ----------------------- Summary Table Window -----------------------
        summary_table_window = sg.Window(title="Summary Table", layout=layout_summary_table_window,
                                         size=(1730, 970), resizable=True, finalize=True,
                                         disable_minimize=True,
                                         location=(90, 0), background_image="backsum.png",
                                         element_padding=(0, 0))
        # ----------------------- Data Quality Table Window -----------------------
        layout_data_quality_table_window = data_quality_table_window_layout()
        data_quality_table_window = sg.Window(title="Data Quality Table",
                                              layout=layout_data_quality_table_window,
                                              size=(1730, 970), resizable=True, finalize=True,
                                              disable_minimize=True,
                                              location=(90, 0), background_image="backsum.png",
                                              element_padding=(0, 0))
        # -------------------------- Graphs Window -----------------------------
        layout_graphs_window = graphs_window_layout()
        graph_window = sg.Window(title="graphs", no_titlebar=False, layout=layout_graphs_window,
                                 size=(1730, 970), resizable=True, finalize=True,
                                 disable_minimize=True,
                                 location=(90, 0), background_image="backsum.png",
                                 element_padding=(0, 0))
        # figure_agg = None
        # fig = PyplotSimple()
        # figure_agg = draw_figure(graph_window['-CANVAS-'].TKCanvas, fig)
        # canvas = FigureCanvasTkAgg(fig)
        graph_window.hide()
        data_quality_table_window.hide()
        while True:
            summary_table_window.element("SumTable").update(values=summary_table_list)  # מונע מהמשתמש לשנות ערכים בטבלה
            event4, values4 = summary_table_window.read()
            if event4 == "SumTable":
                if values4["SumTable"] == [0]:
                    print("row1")
            if event4 == "summary exit" or event4 == sg.WIN_CLOSED:
                break
            if event4 == 'Export to CSV':
                exportCSV(values4)
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
                        graph_window['combo_ride_graph2'].update(visible=False)
                        choose_graph_flag = False
                        break

                    if event5 == "CONTINUE_GRAPH":
                        if values5["avg bpm 1 par"] and choose_graph_flag:
                            # שמירת האינפוטים במשתנים
                            participant_num_input = int(values5['combo_par_graph1'])
                            ride_input = int(values5['combo_ride_graph1'])
                            p1 = Process(target=draw_plot1,
                                         args=(participant_num_input, ride_input, globals.summary_table))
                            p1.start()
                            choose_graph_flag = False

                        elif values5["rmssd for several par"] and choose_graph_flag:
                            # לבדוק האם הנבדקים שנכתבו תואמים לקלט במסך הפתיחה
                            participants_input = values5['combo_par_graph2']
                            ride_input = int(values5['combo_ride_graph2'])
                            p2 = Process(target=draw_plot2,
                                         args=(participants_input, ride_input, globals.summary_table))
                            p2.start()
                            choose_graph_flag = False

                        else:
                            sg.popup_quick_message('Please choose graph before continue',
                                                   font=("Century Gothic", 14), background_color='red',
                                                   location=(970, 880))
            if event4 == "dq button":
                summary_table_window.hide()
                data_quality_table_window.un_hide()
                while True:
                    event6, values6 = data_quality_table_window.read()
                    if event6 == "dq back":
                        data_quality_table_window.hide()
                        summary_table_window.un_hide()
                        break

        data_quality_table_window.close()
        graph_window.close()
        summary_table_window.close()


if __name__ == '__main__':
    ui()
