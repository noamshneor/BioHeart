import time
import threading
import pandas
import numpy as np
import os
import PySimpleGUIQt as sg
import sys
from multiprocessing import Process
import HRV_METHODS
import globals
from EARLY_P_FUNCTIONS import rr_time_match, initial_list_of_existing_par, filling_summary_table, \
    early_process_rr, save_pickle, dq_completeness_bpm, avg_med_bpm, early_process_ecg_sim, early_process_base, \
    initial_data_quality, dq_completeness_rr, med_rr, filling_dq_table, flag_match_exec, fix_min_rr, fix_min_bpm, \
    make_par_group_list
from UI_FUNCTIONS import checkFolders_of_rides, checkFolders_of_base, \
    exportCSV_summary, add_files_in_folder, checkFiles_of_rides, checkFiles_of_base, checks_boundaries, initial_tree, \
    exportCSV_dq, loading_window_update, all_input_0_9, sync_handle, save_input_open_window, tree_handle, \
    exceptions_checkbox_handle, create_empty_folders, pickle_folders, windows_initialization_part_1, \
    windows_initialization_part_2, initial_optional, check_optional_window, check_if_can_continue, plot_HR_with_scenarios, \
    plot_HR_rides, plot_HR_groups_rides, plot_HR_groups_scenarios


# --------------------------------------------- early_process ---------------------------------------------
def early_process():
    """
    A function that arranges the raw files
    (adds columns, matches the scenario column by times for all the files)
    and performs the processing of the files. The output is a summary table with the avg heart rate
     and the heart rate variance
    """
    globals.current_par = 0
    globals.current_ride = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed

    for par in globals.list_of_existing_par:  # loop for participants that exist
        group_list = make_par_group_list(par)
        print("par in list_of_existing_par:" + str(par))
        for filename in os.listdir(globals.main_path + "\\" + "ride 1" + "\\" + "ecg"):
            print("the filename in ecg:" + filename)
            if str(par) in filename:  # אם המספר של המשתתף מרשימת המשתתפים הקיימים מופיע בשם הקובץ בecg
                index_in_folder = os.listdir(globals.main_path + "\\" + "ride 1" + "\\" + "ecg").index(
                    filename)  # באיזה אינדקס מבין הרשימה של הקבצים בecg מופיע הקובץ filename
                print(index_in_folder)  # checked
                for ride in range(1, globals.par_ride_num + 1):  # loop for rides
                    print("Start early process for ride: " + str(ride) + " for par: " + str(par))
                    # -------------------------------------------- ECG & SIM -----------------------------------------
                    list_of_bpm_flag, parECG, parSIM = early_process_ecg_sim(index_in_folder, ride)
                    initial_data_quality()
                    globals.current_ride = ride - 1
                    # filling column 'flag' in parECG, and filling list_of_bpm_flag by scenario.
                    print("flag_match_exec(parECG, parSIM, list_of_bpm_flag, 'BPM')")
                    flag_match_exec(parECG, parSIM, list_of_bpm_flag, 'BPM')
                    fix_min_bpm()
                    listBPM, listBPM_per_scenario = avg_med_bpm(list_of_bpm_flag)
                    dq_completeness_bpm(listBPM_per_scenario)
                    # ------------------------------------------------ RR --------------------------------------------
                    parRR, list_of_rr_flag = early_process_rr(index_in_folder, ride)
                    rr_time_match(parRR)  # function that fill the time column in parRR
                    # filling column 'flag' in parRR, and filling list_of_rr_flag by scenario.
                    print("flag_match_exec(parRR, parSIM, list_of_rr_flag, 'RRIntervals')")
                    flag_match_exec(parRR, parSIM, list_of_rr_flag, 'RRIntervals')
                    fix_min_rr()
                    # ------------------------------------------ BASE RR & ECG ---------------------------------------
                    avg_base, baseRR, baseECG = early_process_base(index_in_folder)
                    # ------------------------------------------------------------------------------------------------
                    # convert to pickle the "clean files"
                    save_pickle(baseECG, baseRR, par, parECG, parRR, parSIM, ride)
                    # ------------------------------------- filling summary table ------------------------------------
                    filling_summary_table(avg_base, baseRR, listBPM, par, list_of_rr_flag, ride, group_list)
                    # ----------------------------------- filling data quality table ---------------------------------
                    med_rr(list_of_rr_flag)
                    dq_completeness_rr()
                    filling_dq_table(listBPM_per_scenario, par, ride, group_list)

                    globals.percent += (1 / len(globals.list_of_existing_par)) / globals.par_ride_num
                    globals.current_ride += 1
                globals.current_par += 1  # עוברים על הקובץ השני בתיקית ecg וכך הלאה
        print(globals.percent * 100)


def pickle_early_process():
    """
    A function that arranges the "clean" pickles files and performs the processing of the files.
    The output is a summary table with the avg heart rate and the heart rate variance
    """
    globals.current_par = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed

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
            # print(summary_table_par[['Participant', 'Ride Number', 'Subtraction BPM','Subtraction RMSSD','Subtraction SDNN','Subtraction SDSD','Subtraction PNN50']])
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
    correct_open_window, correct_optional_window, correct_path_window, exceptions_values_window, exclude_correct, finish_while_loop, group_correct, layout_loading_window, newload, open_window, optional_window, path_load_window = windows_initialization_part_1()
    # -------------------------------------------- Open Windows --------------------------------------------
    while True:  # Create an event loop
        event, values = open_window.read()
        open_window.bring_to_front()
        if event == "EXIT_OPEN" or event == sg.WIN_CLOSED:
            # End program if user closes window or presses the EXIT button
            return False  # אפשר לעצור את הלולאה והחלון ייסגר
        # הגבלת השדות לקבל אך ורק ספרות בין 0 ל9 ללא שום תווים אחרים
        all_input_0_9(event, open_window, values)
        if event == 'Sync':
            sync_handle(open_window, values)
        if event == "CONTINUE_OPEN":
            # ----------------------------------------- SAVE INPUT -----------------------------------------
            if (not values['par_num']) or (not values['scenario_num']) or (
                    not values['scenario_col_num']) or (
                    not values['Sync'] and (not values['sim_start']) or (not values['ecg_start'])):
                # בדיקה האם אחד מ3 השדות לפחות לא מלא
                sg.popup_quick_message('Please fill in all the fields', font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880))
            else:  # כולם מלאים
                if not values['Sync'] and ((values['sim_start'] != "0") and (values['ecg_start'] != "0")):
                    sg.popup_quick_message('At least one of the simulator/ECG fields must start from 0',
                                           font=("Century Gothic", 14), background_color='red', location=(970, 880),
                                           auto_close_duration=5)
                else:
                    # שמירת האינפוטים במשתנים
                    save_input_open_window(values)
                    initial_list_of_existing_par()
                    correct_open_window = True  # כל הפרטים במסך נכונים, אפשר להמשיך למסך הבא

        if correct_open_window:  # רק אם כל הפרטים היו נכונים ונשמרו במסך הקודם
            # כלומר - אם החלון הקודם נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
            optional_window.un_hide()
            open_window.hide()
            # ------------------------------------------- OPTIONAL Window ---------------------------------
            initial_optional(optional_window)
            while True:
                event9, values9 = optional_window.read()
                if event9 == sg.WIN_CLOSED:
                    return False
                if event9 == 'Ex par CB':
                    if values9['Ex par CB']:
                        optional_window.element('Ex par LB').update(disabled=False)
                        optional_window.element('Exclude_OPTIONAL').update(visible=True)
                    else:
                        optional_window.element('Ex par LB').update(disabled=True)
                        optional_window.element('Exclude_OPTIONAL').update(visible=False)
                        globals.par_not_existing = []
                        initial_optional(optional_window)
                if event9 == 'groups CB':
                    if values9['groups CB']:
                        optional_window.element('groups num').update(disabled=False)
                        optional_window.element('Choose_OPTIONAL').update(visible=True)
                    else:
                        optional_window.element('groups num').update(disabled=True)
                        optional_window.element('Choose_OPTIONAL').update(visible=False)
                        globals.group_num = 0
                        for i in list(range(1, 6)):
                            optional_window.element('group' + str(i)).update(visible=False)

                if event9 == 'Exclude_OPTIONAL':
                    globals.par_not_existing = values9['Ex par LB']
                    initial_list_of_existing_par()
                    optional_window.element('Ex par LB').update(globals.list_of_existing_par)
                    for i in list(range(1, 6)):
                        optional_window.element('group' + str(i)).update(globals.list_of_existing_par)

                if event9 == 'Choose_OPTIONAL':
                    globals.group_num = int(values9['groups num'])
                    list_groups = list(range(1, globals.group_num + 1))
                    for i in list_groups:
                        optional_window.element('group' + str(i)).update(visible=True)

                if event9 == 'CONTINUE_OPTIONAL':
                    correct_optional_window = check_optional_window(correct_optional_window, exclude_correct,
                                                                    group_correct, values9)
                if event9 == "BACK_OPTIONAL":
                    optional_window.hide()
                    open_window.un_hide()
                    correct_open_window = False  # בשביל שתתבצע שוב בדיקה על התיקייה אם בוחרים שוב

                    break
                if correct_optional_window:
                    # -------------------------------------------- Path Load Windows --------------------------------------------
                    path_load_window.un_hide()
                    optional_window.hide()
                    initial_tree(path_load_window['-TREE-'], "")
                    while True:
                        event2, values2 = path_load_window.read()
                        if event2 == sg.WIN_CLOSED:
                            return False
                        if event2 == "Create empty folders":
                            create_empty_folders()
                        if event2 == "-MAIN FOLDER-":
                            tree_handle(path_load_window, values2)
                        if event2 == "CONTINUE_PATH":
                            correct_path_window, newload = check_if_can_continue(correct_path_window, newload, values2)
                        if event2 == "BACK_PATH":
                            optional_window.un_hide()
                            path_load_window.hide()
                            correct_optional_window = False
                            correct_path_window = False
                            break
                        if correct_path_window:
                            exceptions_values_window.un_hide()
                            path_load_window.hide()
                            # אם החלון נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
                            # ------------------------------------------- EXCEPTIONS VALUES Window ---------------------------------
                            while True:
                                event8, values8 = exceptions_values_window.read()
                                if event8 == sg.WIN_CLOSED:
                                    return False

                                exceptions_checkbox_handle(event8, exceptions_values_window, values8)

                                if event8 == "CONTINUE_EXCEPTIONS":
                                    if values8["no filtering checkbox"]:
                                        # שמירת האינפוטים במשתנים
                                        globals.filter_type = globals.Filter.NONE
                                        finish_while_loop = True
                                        exceptions_values_window.close()
                                        break
                                    else:
                                        if values8["checkbox exceptions RR"] and not values8["checkbox exceptions BPM"]:
                                            globals.RR_lower = float(values8['_SPIN_RR_LOWER'])
                                            globals.RR_upper = float(values8['_SPIN_RR_UPPER'])
                                            if checks_boundaries(globals.RR_lower, globals.RR_upper):
                                                globals.filter_type = globals.Filter.RR
                                                finish_while_loop = True
                                                break
                                            else:
                                                sg.popup_quick_message(
                                                    'Error! Notice that the lower RR limit must be smaller than the upper RR limit',
                                                    font=("Century Gothic", 10),
                                                    background_color='white', text_color='red', location=(670, 655))

                                        if values8["checkbox exceptions BPM"] and not values8["checkbox exceptions RR"]:
                                            globals.BPM_lower = int(values8['_SPIN_BPM_LOWER'])
                                            globals.BPM_upper = int(values8['_SPIN_BPM_UPPER'])
                                            if checks_boundaries(globals.BPM_lower, globals.BPM_upper):
                                                globals.filter_type = globals.Filter.BPM
                                                finish_while_loop = True
                                                break
                                            else:
                                                sg.popup_quick_message(
                                                    'Error! Notice that the lower BPM limit must be smaller than the upper BPM limit',
                                                    font=("Century Gothic", 10),
                                                    background_color='white', text_color='red', location=(670, 655))

                                        if values8["checkbox exceptions BPM"] and values8["checkbox exceptions RR"]:
                                            globals.RR_lower = float(values8['_SPIN_RR_LOWER'])
                                            globals.RR_upper = float(values8['_SPIN_RR_UPPER'])
                                            globals.BPM_lower = int(values8['_SPIN_BPM_LOWER'])
                                            globals.BPM_upper = int(values8['_SPIN_BPM_UPPER'])
                                            if checks_boundaries(globals.BPM_lower, globals.BPM_upper) and checks_boundaries(
                                                    globals.RR_lower, globals.RR_upper):
                                                globals.filter_type = globals.Filter.BOTH
                                                finish_while_loop = True
                                                break
                                            else:
                                                sg.popup_quick_message(
                                                    'Error! Notice that the lower limits must be smaller than the upper limits',
                                                    font=("Century Gothic", 10),
                                                    background_color='white', text_color='red', location=(670, 655))
                                if event8 == "BACK_EXCEPTIONS":
                                    exceptions_values_window.hide()
                                    path_load_window.un_hide()
                                    correct_path_window = False  # בשביל שתתבצע שוב בדיקה על התיקייה אם בוחרים שוב
                                    finish_while_loop = False
                                    break

                            print(globals.filter_type)
                            print(globals.RR_lower, globals.RR_upper, globals.BPM_lower, globals.BPM_upper)
                        if finish_while_loop:
                            exceptions_values_window.close()
                            path_load_window.close()
                            break
                if finish_while_loop:
                    break
        if finish_while_loop:
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
                event3, values3 = loading_window.read(timeout=1)
                # ---------------------------------- update window elements ----------------------------------
                loading_window_update(loading_window, start_time)
                if globals.percent * 100 >= 99.9:
                    loading_window_update(loading_window, start_time)
                    time.sleep(3)
                    break
                if event3 == "p bar cancel" or event3 == sg.WIN_CLOSED:
                    sys.exit()  # יציאה כפויה של התכנית, הטרד מת
            loading_window.close()

        if globals.percent * 100 >= 99.99:  # אם החלון הקודם נסגר והעיבוד באמת הסתיים, אפשר להציג את החלון הבא
            data_quality_table_window, dq_table_list, graph_window, summary_table_list, summary_table_window = windows_initialization_part_2()
            do_restart = False
            while True:
                summary_table_window.element("SumTable").update(
                    values=summary_table_list)  # מונע מהמשתמש לשנות ערכים בטבלה
                event4, values4 = summary_table_window.read()
                if event4 == "summary exit" or event4 == sg.WIN_CLOSED:
                    break
                if event4 == "Restart button":
                    do_restart = True
                    break
                if event4 == 'Export to CSV':
                    exportCSV_summary(values4)
                if event4 == "Graphs button":
                    summary_table_window.hide()
                    graph_window.un_hide()
                    # choose_graph_flag = True
                    while True:
                        y_axis_choose = True
                        x_axis_choose = True
                        rides_choose = True
                        scenarios_choose = True
                        participants_choose = True
                        event5, values5 = graph_window.read()
                        graph_window.bring_to_front()
                        # print(event5)
                        # if not values5["avg bpm 1 par"] and not values5["rmssd for several par"]:  # אם שניהם לא לחוצים
                        #    choose_graph_flag = False
                        # else:
                        #    choose_graph_flag = True

                        if event5 == "custom graph":#WORKS
                            #graph_window.FindElement('y axis').Update(values=globals.hrv_methods_list)
                            graph_window.FindElement('scenarios listbox').Update(disabled=False)
                            graph_window.FindElement('rides listbox').Update(disabled=False)
                            graph_window.FindElement('y axis').Update(disabled=False)
                            graph_window.FindElement('x axis scenarios').Update(disabled=False)
                            graph_window.FindElement('x axis rides').Update(disabled=False)
                            graph_window.FindElement('bar pars').Update(disabled=False)
                            graph_window.FindElement('bar groups').Update(disabled=False)
                            graph_window["SELECT ALL rides"].update(disabled=False)
                            graph_window["CLEAN ALL rides"].update(disabled=False)
                            graph_window["SELECT ALL sc"].update(disabled=False)
                            graph_window["CLEAN ALL sc"].update(disabled=False)

                        if event5 == "general graph":#WORKS
                            #graph_window.FindElement('y axis').Update(values='Average BPM'.split(','))
                            graph_window.FindElement('scenarios listbox').Update(disabled=True)
                            graph_window.FindElement('rides listbox').Update(disabled=True)
                            graph_window.FindElement('participant listbox').Update(disabled=True)
                            graph_window.FindElement('y axis').Update(disabled=True)
                            graph_window.FindElement('x axis scenarios').Update(disabled=True)
                            graph_window.FindElement('x axis rides').Update(disabled=True)
                            graph_window.FindElement('bar pars').Update(disabled=True)
                            graph_window.FindElement('bar groups').Update(disabled=True)
                            graph_window["SELECT ALL rides"].update(disabled=True)
                            graph_window["CLEAN ALL rides"].update(disabled=True)
                            graph_window["SELECT ALL sc"].update(disabled=True)
                            graph_window["CLEAN ALL sc"].update(disabled=True)

                        if event5 == "x axis rides":#WORKS
                            graph_window.FindElement('rides listbox').Update(disabled=False)
                            graph_window.FindElement('scenarios listbox').Update(disabled=True)
                            graph_window['scenarios listbox'].update("")
                            graph_window['scenarios listbox'].update(globals.scenarios_list)
                            graph_window["SELECT ALL rides"].update(disabled=False)
                            graph_window["CLEAN ALL rides"].update(disabled=False)
                            graph_window["SELECT ALL sc"].update(disabled=True)
                            graph_window["CLEAN ALL sc"].update(disabled=True)

                        if event5 == "x axis scenarios":#WORKS
                            graph_window.FindElement('rides listbox').Update(disabled=True)#להפוך את הנסיעות לבחירה של אחד
                            graph_window["SELECT ALL rides"].update(disabled=True)
                            graph_window["CLEAN ALL rides"].update(disabled=True)
                            graph_window.FindElement('scenarios listbox').Update(disabled=False)
                            graph_window["SELECT ALL sc"].update(disabled=False)
                            graph_window["CLEAN ALL sc"].update(disabled=False)
                            graph_window['rides listbox'].update("")
                            graph_window['rides listbox'].update(globals.scenarios_list)

                        if event5 == "SELECT ALL rides":
                            graph_window['rides listbox'].SetValue(globals.rides_list)
                        if event5 == "CLEAN ALL rides":
                            graph_window['rides listbox'].update("")
                            graph_window['rides listbox'].update(globals.rides_list)

                        if event5 == "SELECT ALL sc":
                            graph_window['scenarios listbox'].SetValue(globals.scenarios_list)
                        if event5 == "CLEAN ALL sc":
                            graph_window['scenarios listbox'].update("")
                            graph_window['scenarios listbox'].update(globals.scenarios_list)

                        if event5 == "graphs back":
                            graph_window.hide()
                            summary_table_window.un_hide()
                            #                  choose_graph_flag = False
                            break

                        if event5 == "CONTINUE_GRAPH":
                            if values5["custom graph"]:
                                if not values5['y axis']:  # אם לא נבחר מדד מהרשימת מדדים
                                    sg.popup_quick_message('You have to choose Y axis!',
                                                           font=("Century Gothic", 14), background_color='red',
                                                           location=(970, 880))
                                    y_axis_choose = False
                                if not values5["scenarios listbox"]:  # לא נבחרו תרחישים
                                    sg.popup_quick_message('You have to choose specific scenarios!',
                                                           font=("Century Gothic", 14), background_color='red',
                                                           location=(970, 880))
                                    scenarios_choose = False



                                if values5["x axis rides"]:#נסיעות
                                    if not values5['rides listbox']:  # אבל לא נבחרו בליסטבוקס משתתפים להציג
                                        sg.popup_quick_message('You have to choose specific rides!',
                                                               font=("Century Gothic", 14), background_color='red',
                                                               location=(970, 880))
                                        rides_choose = False
                                    else:  # נבחרו נסיעות מסוימות בליסטבוקס
                                        if y_axis_choose and scenarios_choose and rides_choose:  # קוד כפול
                                            axis_y_methods_input = values5['y axis']
                                            axis_x_scenarios_input = values5['scenarios listbox']
                                            rides_input = values5['rides listbox']

                                            if values5["bar pars"]:
                                                if not values5['participant listbox']:  # לא נבחרו משתתפים
                                                    sg.popup_quick_message('You have to choose specific participants!',
                                                                           font=("Century Gothic", 14),
                                                                           background_color='red',
                                                                           location=(970, 880))
                                                    participants_choose = False
                                                else:#נבחרו משתתפים
                                                    if len(values5['participant listbox']) > 5:
                                                        sg.popup_quick_message(
                                                            'You have to choose up to 5 participants!',
                                                            font=("Century Gothic", 14),
                                                            background_color='red',
                                                            location=(970, 880))
                                                    else:#נבחרו עד 5 משתתפים
                                                        bar_participants_input = values5['participant listbox']
                                                        if values5["baseline checkbox"]:
                                                            print("axis y:" + str(
                                                                axis_y_methods_input) + " ,axis x of rides: " + str(
                                                                rides_input) + " and baseline, in scenarios: " + str(
                                                                axis_x_scenarios_input))
                                                            print("תוציא את גרף p4 עם נסיעות בציר איקס ובעמודות משתתפים ובייסלין")
                                                            p4 = Process(target=plot_HR_rides, args=(
                                                                globals.list_of_existing_par, rides_input,
                                                                globals.summary_table))
                                                            p4.start()
                                                        else:#בלי בייסלין
                                                                print( "axis y:"+str(axis_y_methods_input) + " ,axis x of rides: " + str(
                                                                    rides_input) + " in scenarios: " + str(axis_x_scenarios_input))
                                                                print("תוציא את גרף p4 עם נסיעות בציר איקס ובעמודות משתתפים")

                                            else: #נבחרו קבוצות
                                                if values5["baseline checkbox"]:
                                                    print("axis y:" + str(
                                                        axis_y_methods_input) + " ,axis x of rides: " + str(
                                                        rides_input) + " and baseline, in scenarios: " + str(
                                                        axis_x_scenarios_input)+" with groups")
                                                    print(
                                                        "תוציא את גרף p6 עם נסיעות בציר איקס ובעמודות קבוצות ובייסלין")

                                                else:  # בלי בייסלין
                                                    print("axis y:" + str(
                                                        axis_y_methods_input) + " ,axis x of rides: " + str(
                                                        rides_input) + " and baseline, in scenarios: " + str(
                                                        axis_x_scenarios_input) + " with groups")
                                                    print(
                                                        "תוציא את גרף p6 עם נסיעות בציר איקס ובעמודות קבוצות ובייסלין")
                                                    p6 = Process(target=plot_HR_groups_rides, args=(
                                                        axis_x_scenarios_input, globals.group_num, rides_input,
                                                        globals.summary_table))
                                                    p6.start()
                                if values5["x axis scenarios"]:  # אם בחרתי תרחישים בציר איקס
                                        if y_axis_choose and scenarios_choose:  # קוד כפול
                                            axis_y_methods_input = values5['y axis']
                                            axis_x_scenarios_input = values5['scenarios listbox']
                                            if values5["bar pars"]:
                                                if not values5['participant listbox']:  # לא נבחרו משתתפים
                                                    sg.popup_quick_message('You have to choose specific participants!',
                                                                           font=("Century Gothic", 14),
                                                                           background_color='red',
                                                                           location=(970, 880))
                                                    participants_choose = False
                                                else:  # נבחרו משתתפים
                                                    if len(values5['participant listbox']) > 5:
                                                        sg.popup_quick_message(
                                                            'You have to choose up to 5 participants!',
                                                            font=("Century Gothic", 14),
                                                            background_color='red',
                                                            location=(970, 880))
                                                    else:  # נבחרו עד 5 משתתפים
                                                        bar_participants_input = values5['participant listbox']
                                                        if values5["baseline checkbox"]:
                                                            print("axis y:" + str(
                                                                axis_y_methods_input) + " ,axis x scenarios: " + str(
                                                                axis_x_scenarios_input))
                                                            print(
                                                                "תוציא את גרף p3 עם תרחישים בציר איקס ובעמודות משתתפים ובייסלין")
                                                            p3 = Process(target=plot_HR_with_scenarios, args=(
                                                                 axis_x_scenarios_input, globals.list_of_existing_par,
                                                                 globals.summary_table))
                                                            p3.start()

                                                        else:  # בלי בייסלין
                                                            print("axis y:" + str(
                                                                axis_y_methods_input) + " ,axis x scenarios: " + str(
                                                                axis_x_scenarios_input) + " in scenarios: ")
                                                            print(
                                                                "תוציא את גרף p4 עם נסיעות בציר איקס ובעמודות משתתפים")

                                            else:#בחרתי קבוצות ותרחישים
                                                if values5["baseline checkbox"]:
                                                    print("axis y:" + str(
                                                        axis_y_methods_input) + " ,axis x of scenarios: " + str(
                                                        axis_x_scenarios_input) + " and baseline, with groups")
                                                    print(
                                                        "תוציא את גרף p5 עם תרחישים בציר איקס ובעמודות קבוצות ובייסלין")

                                                else:  # בלי בייסלין
                                                    print("axis y:" + str(
                                                        axis_y_methods_input) + " ,axis x of rides: " + str(
                                                        rides_input) + " and baseline, in scenarios: " + str(
                                                        axis_x_scenarios_input) + " with groups")
                                                    print(
                                                        "תוציא את גרף p5 עם תרחישים בציר איקס ובעמודות קבוצות")
                                                    p5 = Process(target=plot_HR_groups_scenarios,
                                                                 args=(axis_x_scenarios_input,
                                                                       globals.group_num,
                                                                       globals.summary_table))
                                                    p5.start()

                            else: #choose general graphs
                                print("לצייר גרף אחרון")
            ########################################################################################

            # elif values5["rmssd for several par"] and choose_graph_flag:
            #     # לבדוק האם הנבדקים שנכתבו תואמים לקלט במסך הפתיחה
            #     participants_input = values5['combo_par_graph2']
            #     ride_input = int(values5['combo_ride_graph2'])
            #     p2 = Process(target=draw_plot2,
            #                  args=(participants_input, ride_input, globals.summary_table))
            #     p2.start()
            #     choose_graph_flag = False
            #
            # else:
            #     sg.popup_quick_message('Please choose graph before continue',
            #                            font=("Century Gothic", 14), background_color='red',
            #                            location=(970, 880))

                if event4 == "dq button":
                    summary_table_window.hide()
                    data_quality_table_window.un_hide()
                    data_quality_table_window.element("dq export").update(visible=True)
                    while True:
                        data_quality_table_window.element("DataQTable").update(
                            values=dq_table_list)  # מונע מהמשתמש לשנות ערכים בטבלה
                        event6, values6 = data_quality_table_window.read()
                        data_quality_table_window.bring_to_front()
                        if event6 == "dq back":
                            data_quality_table_window.hide()
                            summary_table_window.un_hide()
                            break
                        if event6 == "dq export":
                            exportCSV_dq()
                if event4 == "SumTable":
                    if values4["SumTable"]:
                        line = [dq_table_list[values4["SumTable"][0]]]
                        summary_table_window.hide()
                        data_quality_table_window.un_hide()
                        data_quality_table_window.element("dq export").update(visible=False)
                        while True:
                            data_quality_table_window.element("DataQTable").update(
                                values=line)  # מונע מהמשתמש לשנות ערכים בטבלה
                            event7, values7 = data_quality_table_window.read()
                            if event7 == "dq back":
                                data_quality_table_window.hide()
                                summary_table_window.un_hide()
                                break
            open_window.close()
            data_quality_table_window.close()
            graph_window.close()
            summary_table_window.close()
            return do_restart


if __name__ == '__main__':
    restart = ui()
    if restart:
        os.system('main.py')
        exit()
    else:
        sys.exit(0)
    """
    # -------------------------- Graphs Window -----------------------------
    layout_graphs_window = graphs_window_layout()
    graph_window = sg.Window(title="Graphs", no_titlebar=True, layout=layout_graphs_window,
                             size=(1730, 970), resizable=True, finalize=True,
                             disable_minimize=True,
                             location=(90, 20), background_image="backsum.png",
                             element_padding=(0, 0))
    while True:
        event5, values5 = graph_window.read()
        if event5 == "HV":
            graph_window.FindElement('y axis').Update(values='Average BPM'.split(','))

    graph_window.close()

    #RR_hara = pandas.read_pickle("pickle_parRR1")
    #hara2 = RR_hara.to_csv('RR_with_time_and_scenario.csv')



    
    layout_exceptions_values_window = exceptions_values_layout()
    # ------------------------------------------- EXCEPTIONS VALUES Window ---------------------------------
    exceptions_values_window = sg.Window(title="Filter Exceptional Values", layout=layout_exceptions_values_window,
                                         size=(1000, 680),
                                         disable_minimize=True,
                                         location=(450, 120), background_image="backsum.png", element_padding=(0, 0),
                                         finalize=True)
    while True:
        event8, values8 = exceptions_values_window.read()
        if event8 == sg.WIN_CLOSED:
            break

    """
