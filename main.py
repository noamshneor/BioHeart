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
    initial_data_quality, dq_completeness_rr, med_rr, filling_dq_table, flag_match_exec
from LAYOUT_UI import graphs_window_layout, data_quality_table_window_layout, summary_table_window_layout, \
    loading_window_layout, path_load_window_layout, open_window_layout, exceptions_values_layout
from UI_FUNCTIONS import draw_plot1, draw_plot2, early_table, checkFolders_of_rides, checkFolders_of_base, \
    exportCSV_summary, add_files_in_folder, checkFiles_of_rides, checkFiles_of_base, checks_boundaries, initial_tree, \
    exportCSV_dq, loading_window_update, all_input_0_9, sync_handle, save_input_open_window, tree_handle, \
    exceptions_checkbox_handle, create_empty_folders


# --------------------------------------------- early_process ---------------------------------------------
def early_process():
    """
    A function that arranges the raw files
    (adds columns, matches the scenario column by times for all the files)
    and performs the processing of the files. The output is a summary table with the avg heart rate
     and the heart rate variance
    """
    globals.current_par = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed
    initial_list_of_existing_par()

    for par in globals.list_of_existing_par:  # loop for participants that exist
        print("par in list_of_existing_par:" + str(par))
        for filename in os.listdir(globals.main_path + "\\" + "ride 1" + "\\" + "ecg"):
            print("the filename in ecg:" + filename)
            if str(par) in filename:  # אם המספר של המשתתף מרשימת המשתתפים הקיימים מופיע בשם הקובץ בecg
                index_in_folder = os.listdir(globals.main_path + "\\" + "ride 1" + "\\" + "ecg").index(
                    filename)  # באיזה אינדקס מבין הרשימה של הקבצים בecg מופיע הקובץ filename
                print(index_in_folder)  # checked
                for ride in range(1, globals.par_ride_num + 1):  # loop for rides
                    print("Start early process for ride: " + str(ride) + " for par: " + str(par))
                    globals.current_ride = ride - 1
                    # -------------------------------------------- ECG & SIM -----------------------------------------
                    list_of_bpm_flag, parECG, parSIM = early_process_ecg_sim(index_in_folder, ride)
                    initial_data_quality()
                    # filling column 'flag' in parECG, and filling list_of_bpm_flag by scenario.
                    print("flag_match_exec(parECG, parSIM, list_of_bpm_flag, 'BPM')")
                    flag_match_exec(parECG, parSIM, list_of_bpm_flag, 'BPM')
                    listBPM, listBPM_per_scenario = avg_med_bpm(list_of_bpm_flag)
                    dq_completeness_bpm(listBPM_per_scenario)
                    # ------------------------------------------------ RR --------------------------------------------
                    parRR, list_of_rr_flag = early_process_rr(index_in_folder, ride)
                    rr_time_match(parRR)  # function that fill the time column in parRR
                    # filling column 'flag' in parRR, and filling list_of_rr_flag by scenario.
                    print("flag_match_exec(parRR, parSIM, list_of_rr_flag, 'RRIntervals')")
                    flag_match_exec(parRR, parSIM, list_of_rr_flag, 'RRIntervals')
                    # ------------------------------------------ BASE RR & ECG ---------------------------------------
                    avg_base, baseRR, baseECG = early_process_base(index_in_folder)
                    # ------------------------------------------------------------------------------------------------
                    # convert to pickle the "clean files"
                    save_pickle(baseECG, baseRR, par, parECG, parRR, parSIM, ride)
                    # ------------------------------------- filling summary table ------------------------------------
                    filling_summary_table(avg_base, baseRR, listBPM, par, parRR, ride)
                    # ----------------------------------- filling data quality table ---------------------------------
                    med_rr(list_of_rr_flag)
                    dq_completeness_rr()
                    filling_dq_table(listBPM_per_scenario, par, ride)

                    globals.percent += (1 / len(globals.list_of_existing_par)) / globals.par_ride_num
                globals.current_par += 1  # עוברים על הקובץ השני בתיקית ecg וכך הלאה
        print(globals.percent * 100)


def pickle_early_process():
    """
    A function that arranges the "clean" pickles files and performs the processing of the files.
    The output is a summary table with the avg heart rate and the heart rate variance
    """
    globals.current_par = 0
    globals.percent = 0  # Displays in percentages for how many participants the final table data has been processed
    initial_list_of_existing_par()

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
    layout_open_window = open_window_layout()
    layout_path_load_window = path_load_window_layout()
    layout_loading_window = loading_window_layout()
    layout_exceptions_values_window = exceptions_values_layout()

    correct_open_window = False  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    correct_path_window = False  # האם כל הפרטים במסך הנתיב מולאו בצורה נכונה
    newload = True  # האם נבחרה טעינה חדשה או לא - טעינה קיימת

    # -------------------------------------------- Open Windows --------------------------------------------
    open_window = sg.Window(title="BIO Heart", layout=layout_open_window, size=(1730, 970), disable_minimize=True,
                            location=(90, 0), background_image="back1.png", element_padding=(0, 0), finalize=True)
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
                    break  # אפשר לעצור את הלולאה והחלון ייסגר
    open_window.close()  # פקודת סגירת חלון ביציאה מהלולאה

    if correct_open_window:  # רק אם כל הפרטים היו נכונים ונשמרו במסך הקודם
        # כלומר - אם החלון הקודם נסגר והכל היה תקין, אפשר להמשיך לחלון הבא
        exceptions_values_window = sg.Window(title="Filter Exceptional Values", layout=layout_exceptions_values_window,
                                             size=(1000, 680),
                                             disable_minimize=True,
                                             location=(5000, 5000), background_image="backsum.png",
                                             element_padding=(0, 0),
                                             finalize=True)
        exceptions_values_window.hide()
        exceptions_values_window.move(450, 120)
        # -------------------------------------------- Path Load Windows --------------------------------------------
        path_load_window = sg.Window(title="BIO Heart", layout=layout_path_load_window, size=(1730, 970),
                                     disable_minimize=True,
                                     location=(90, 0), background_image="back2.png", element_padding=(0, 0),
                                     finalize=True)

        initial_tree(path_load_window['-TREE-'], "")
        exit_path_load = False
        while not exit_path_load:
            event2, values2 = path_load_window.read()
            if event2 == "EXIT" or event2 == sg.WIN_CLOSED:
                return False
            if event2 == "Create empty folders":
                create_empty_folders()
            if event2 == "-MAIN FOLDER-":
                tree_handle(path_load_window, values2)
            if event2 == "CONTINUE_PATH":
                # check if can continue - להפוך לפונקציה
                if not values2["-MAIN FOLDER-"]:  # אם הנתיב ריק ולא נבחר
                    sg.popup_quick_message("Please fill in the Main Folder's field", font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880))
                else:  # אם הנתיב לא ריק
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

            if correct_path_window:
                path_load_window.hide()
                exceptions_values_window.un_hide()
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
                            exit_path_load = True
                            break
                        else:
                            if values8["checkbox exceptions RR"] and not values8["checkbox exceptions BPM"]:
                                globals.RR_lower = float(values8['_SPIN_RR_LOWER'])
                                globals.RR_upper = float(values8['_SPIN_RR_UPPER'])
                                if checks_boundaries(globals.RR_lower, globals.RR_upper):
                                    globals.filter_type = globals.Filter.RR
                                    exit_path_load = True

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
                                    exit_path_load = True
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
                                    exit_path_load = True
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
                        break

                print(globals.filter_type)
                print(globals.RR_lower, globals.RR_upper, globals.BPM_lower, globals.BPM_upper)
        exceptions_values_window.close()
        path_load_window.close()
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
            loading_window_update(loading_window, start_time)
            if globals.percent * 100 >= 99.99:
                break
            if event3 == "p bar cancel" or event3 == sg.WIN_CLOSED:
                sys.exit()  # יציאה כפויה של התכנית, הטרד מת
        loading_window.close()

    if globals.percent * 100 >= 99.99:  # אם החלון הקודם נסגר והעיבוד באמת הסתיים, אפשר להציג את החלון הבא
        # ----------------------- Early Summary Table -----------------------
        summary_table_list = early_table("summary_table")  # עיבוד מקדים לטבלה
        layout_summary_table_window = summary_table_window_layout(
            summary_table_list)  # יצירת הלייאאוט עם הרשימה המעודכנת של הטבלה
        dq_table_list = early_table("data_quality_table")  # עיבוד מקדים לטבלה
        layout_data_quality_table_window = data_quality_table_window_layout(
            dq_table_list)  # יצירת הלייאאוט עם הרשימה המעודכנת של הטבלה
        # ----------------------- Data Quality Table Window -----------------------
        data_quality_table_window = sg.Window(title="Data Quality Table",
                                              layout=layout_data_quality_table_window,
                                              size=(1730, 970), resizable=True, finalize=True,
                                              disable_minimize=True, no_titlebar=True,
                                              location=(90, 20), background_image="backsum.png",
                                              element_padding=(0, 0))
        data_quality_table_window.hide()
        # -------------------------- Graphs Window -----------------------------
        layout_graphs_window = graphs_window_layout()
        graph_window = sg.Window(title="Graphs", no_titlebar=False, layout=layout_graphs_window,
                                 size=(1730, 970), resizable=True, finalize=True,
                                 disable_minimize=True,
                                 location=(90, 20), background_image="backsum.png",
                                 element_padding=(0, 0))
        graph_window.hide()
        # ----------------------- Summary Table Window -----------------------
        summary_table_window = sg.Window(title="Summary Table", layout=layout_summary_table_window,
                                         size=(1730, 970), resizable=True, finalize=True,
                                         disable_minimize=True,
                                         location=(90, 0), background_image="backsum.png",
                                         element_padding=(0, 0))
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
                graph_window.FindElement('scenarios listbox').Update(disabled=True)
                while True:
                    y_axis_choose = True
                    x_axis_choose = True
                    rides_choose = True
                    event5, values5 = graph_window.read()
                    graph_window.bring_to_front()
                    # print(event5)
                    #if not values5["avg bpm 1 par"] and not values5["rmssd for several par"]:  # אם שניהם לא לחוצים
                    #    choose_graph_flag = False
                    #else:
                    #    choose_graph_flag = True

                    if event5 == "HV":
                        graph_window.FindElement('y axis').Update(values='Average BPM'.split(','))

                    if event5 == "HRV":
                        graph_window.FindElement('y axis').Update(values=globals.hrv_methods_list)

                    if event5 == "x axis par":
                        graph_window.FindElement('scenarios listbox').Update(disabled=True)
                        graph_window['scenarios listbox'].update("")
                        graph_window['scenarios listbox'].update(globals.scenarios_list)
                        graph_window["SELECT ALL par"].update(disabled=False)
                        graph_window["CLEAN ALL par"].update(disabled=False)
                        graph_window.FindElement('participant listbox').Update(disabled=False)
                        graph_window["SELECT ALL sc"].update(disabled=True)
                        graph_window["CLEAN ALL sc"].update(disabled=True)
                    if event5 == "x axis scenarios":
                        graph_window.FindElement('participant listbox').Update(disabled=True)
                        graph_window['participant listbox'].update("")
                        graph_window['participant listbox'].update(globals.list_of_existing_par)
                        graph_window["SELECT ALL par"].update(disabled=True)
                        graph_window["CLEAN ALL par"].update(disabled=True)
                        graph_window.FindElement('scenarios listbox').Update(disabled=False)
                        graph_window["SELECT ALL sc"].update(disabled=False)
                        graph_window["CLEAN ALL sc"].update(disabled=False)

                    if event5 == "SELECT ALL par":
                        graph_window['participant listbox'].SetValue(globals.list_of_existing_par)
                    if event5 == "CLEAN ALL par":
                        graph_window['participant listbox'].update("")
                        graph_window['participant listbox'].update(globals.list_of_existing_par)

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
                        if not values5['y axis']:  # אם לא נבחר מדד מהרשימת מדדים
                            sg.popup_quick_message('You have to choose Y axis!',
                                                   font=("Century Gothic", 14), background_color='red',
                                                   location=(970, 880))
                            y_axis_choose = False
                        if not values5["choose rides"]:  # לא נבחרו נסיעות בליסטבוקס
                            sg.popup_quick_message('You have to choose specific rides!',
                                                   font=("Century Gothic", 14), background_color='red',
                                                   location=(970, 880))
                            rides_choose = False

                        if values5["x axis par"]:
                            if not values5['participant listbox']:  # אבל לא נבחרו בליסטבוקס משתתפים להציג
                                sg.popup_quick_message('You have to choose specific participants!',
                                                       font=("Century Gothic", 14), background_color='red',
                                                       location=(970, 880))
                                x_axis_choose = False
                            else: #נבחר משתתפים בליסטבוקס
                                axis_x_participants_input = values5['participant listbox']
                                if y_axis_choose and rides_choose and x_axis_choose:#קוד כפול
                                    axis_y_methods_input = values5['y axis']
                                    rides_input = values5['choose rides']
                                    if values5["baseline checkbox"]:
                                        if values5["HRV"]:
                                            print("HRV methods: " + str(
                                                axis_y_methods_input) + "with baseline and axis x of participants: " + str(
                                                axis_x_participants_input) + " in rides: " + str(rides_input))
                                        else:#HR
                                            print("HR methods: " + str(
                                                axis_y_methods_input) + "with baseline and axis x of participants: " + str(
                                                axis_x_participants_input) + " in rides: " + str(rides_input))
                                    else: #לא נבחר בייסלין
                                       if values5["HRV"]:
                                           print("HRV method: " + str(
                                               axis_y_methods_input) + " and axis x of participants: " + str(
                                               axis_x_participants_input) + " in rides: " + str(rides_input))
                                       else:
                                           print("HR method: " + str(
                                               axis_y_methods_input) + " and axis x of participants: " + str(
                                               axis_x_participants_input) + " in rides: " + str(rides_input))


                        if values5["x axis scenarios"]:  # אם בחרתי תרחישים בציר איקס
                            if not values5['scenarios listbox']:  # אבל לא נבחרו בליסטבוקס תרחישים להציג
                                sg.popup_quick_message('You have to choose specific scenarios!',
                                                       font=("Century Gothic", 14), background_color='red',
                                                       location=(970, 880))
                                x_axis_choose = False
                            else:  # נבחרו בליסטבוקס תרחישים להציג
                                axis_x_scenarios_input = values5['scenarios listbox']
                                if y_axis_choose and rides_choose and x_axis_choose:#קוד כפול
                                    axis_y_methods_input = values5['y axis']
                                    rides_input = values5['choose rides']
                                    if values5["baseline checkbox"]:
                                        if values5["HRV"]:
                                            print("HRV methods: "+str(axis_y_methods_input)+"with baseline and axis x of scenarios: "+str(axis_x_scenarios_input)+" in rides: "+str(rides_input))
                                        else:#HV
                                            print("HR method: "+str(axis_y_methods_input)+"with baseline and axis x of scenarios: "+str(axis_x_scenarios_input)+" in rides: "+str(rides_input))
                                    else:  # לא נבחר בייסלין
                                        if values5["HRV"]:
                                            print("HRV method: " + str(
                                                axis_y_methods_input) + " and axis x of scenarios: " + str(
                                                axis_x_scenarios_input) + " in rides: " + str(rides_input))
                                        else:#HR
                                            print("HR method: " + str(
                                                axis_y_methods_input) + " and axis x of scenarios: " + str(
                                                axis_x_scenarios_input) + " in rides: " + str(rides_input))



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
