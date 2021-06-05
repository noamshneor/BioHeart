import os
import shutil
import threading
import time
import PySimpleGUIQt as sg
import numpy as np
import pandas
from matplotlib import pyplot as plt
import globals
from LAYOUT_UI import open_window_layout, loading_window_layout, path_load_window_layout, exceptions_values_layout, \
    optional_window_layout, summary_table_window_layout, data_quality_table_window_layout, graphs_window_layout


# --------------------------------------------- UI FUNCTIONS ---------------------------------------------
def windows_initialization_part_1():
    """
        A function that initializes all windows up to the loading stage.
    """
    layout_open_window = open_window_layout()
    layout_path_load_window = path_load_window_layout()
    layout_loading_window = loading_window_layout()
    layout_exceptions_values_window = exceptions_values_layout()
    layout_optional_window = optional_window_layout()
    optional_window = sg.Window(title="BIO Heart", layout=layout_optional_window, size=(1730, 970),
                                disable_minimize=True,
                                location=(5000, 5000), background_image="back1.png",
                                element_padding=(0, 0), finalize=True)
    optional_window.hide()
    optional_window.move(90, 0)
    path_load_window = sg.Window(title="BIO Heart", layout=layout_path_load_window, size=(1730, 970),
                                 disable_minimize=True,
                                 location=(5000, 5000), background_image="back2.png", element_padding=(0, 0),
                                 finalize=True)
    path_load_window.hide()
    path_load_window.move(90, 0)
    exceptions_values_window = sg.Window(title="Filter Exceptional Values",
                                         layout=layout_exceptions_values_window,
                                         size=(1000, 680),
                                         disable_minimize=True,
                                         location=(5000, 5000), background_image="backsum.png",
                                         element_padding=(0, 0),
                                         finalize=True)
    exceptions_values_window.hide()
    exceptions_values_window.move(450, 120)
    globals.list_of_existing_par = list(range(1, globals.par_num + 1))
    correct_open_window = False  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    correct_path_window = False  # האם כל הפרטים במסך הנתיב מולאו בצורה נכונה
    newload = True  # האם נבחרה טעינה חדשה או לא - טעינה קיימת
    correct_optional_window = False  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    exclude_correct = True  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    group_correct = True  # האם כל הפרטים במסך הפתיחה מולאו בצורה נכונה
    finish_while_loop = False  # האם הלולאה הסתיימה וצריך לסיים את התוכנית
    open_window = sg.Window(title="BIO Heart", layout=layout_open_window, size=(1730, 970), disable_minimize=True,
                            location=(90, 0), background_image="back1.png", element_padding=(0, 0), finalize=True)
    return correct_open_window, correct_optional_window, correct_path_window, exceptions_values_window, exclude_correct, finish_while_loop, group_correct, layout_loading_window, newload, open_window, optional_window, path_load_window


def initial_optional(optional_window):
    """
        A function that initializes the screen in which subjects are excluded and groups are selected.
        The function initializes the list of subjects wherever it appears on the screen.
    """
    globals.list_of_existing_par = list(range(1, globals.par_num + 1))  # אתחול רשימת הנבדקים
    optional_window.element('Ex par LB').update(globals.list_of_existing_par)
    for i in list(range(1, 6)):
        optional_window.element('group' + str(i)).update(globals.list_of_existing_par)


def check_optional_window(correct_optional_window, exclude_correct, group_correct, values9):
    """
        A function that handles extreme conditions on the optional screen and displays messages accordingly.
    """
    if values9['Ex par CB']:
        if not globals.par_not_existing:
            sg.popup_quick_message(
                "Choose participants and then click on \"Exclude\" OR deselect the checkbox \"Excluded participants\".",
                font=("Century Gothic", 14),
                background_color='red', location=(970, 780), auto_close_duration=6)
            exclude_correct = False
        else:
            exclude_correct = True
    if values9['groups CB']:
        list_groups = list(range(1, globals.group_num + 1))
        list_values = []
        for i in list_groups:
            if not values9['group' + str(i)]:
                sg.popup_quick_message("One or more of the groups was left empty",
                                       font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880), auto_close_duration=5)
                return False
            else:
                list_values += values9['group' + str(i)]
        contains_duplicates = any(list_values.count(element) > 1 for element in list_values)

        if len(globals.list_of_existing_par) < globals.group_num or len(list_values) == 0:
            sg.popup_quick_message(
                "No group is selected! Click \"Choose\" and select all the participants OR deselect the checkbox \"Experimental groups\".",
                font=("Century Gothic", 14),
                background_color='red', location=(970, 880), auto_close_duration=6)
            group_correct = False
        else:
            if contains_duplicates:
                sg.popup_quick_message("Select different participants in each group",
                                       font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880), auto_close_duration=5)
                group_correct = False
            else:
                if set(list_values) != set(globals.list_of_existing_par):
                    sg.popup_quick_message("Select all the participants in groups",
                                           font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880),
                                           auto_close_duration=5)
                    group_correct = False
                else:
                    group_correct = True
    if exclude_correct and group_correct:
        for i in list(range(1, globals.group_num + 1)):
            globals.lists_of_groups.append(values9['group' + str(i)])  # index 0=group1, 1=group2....
        correct_optional_window = True  # כל הפרטים במסך נכונים, אפשר להמשיך למסך הבא
    if not values9['groups CB'] and not values9['Ex par CB']:
        correct_optional_window = True
    return correct_optional_window


def check_if_can_continue(correct_path_window, newload, values2):
    """
        A function that handles extreme situations on the screen where a main folder is selected,
        and displays messages accordingly.
        The function checks if everything is OK in the selected folder and then we can proceed to the next screen.
    """
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
                        pickle_folders()
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
    return correct_path_window, newload


def windows_initialization_part_2():
    """
        A function that initializes all windows from the loading stage to the end of the program.
    """
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
                             size=(865, 970), resizable=True, finalize=True,
                             disable_minimize=True,
                             location=(523, 20), background_image="backsum.png",
                             element_padding=(0, 0))
    graph_window.hide()
    # ----------------------- Summary Table Window -----------------------
    summary_table_window = sg.Window(title="Summary Table", layout=layout_summary_table_window,
                                     size=(1730, 970), resizable=True, finalize=True,
                                     disable_minimize=True,
                                     location=(90, 0), background_image="backsum.png",
                                     element_padding=(0, 0))
    return data_quality_table_window, dq_table_list, graph_window, summary_table_list, summary_table_window


# def plot1(participant_num_input, ride_input, table):
#     x = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Scenario']]
#     print(x)
#     y = table.loc[
#         (table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Average BPM']]
#     print(y)
#     plt.plot(x, y, marker='.')
#     plt.title('AVG BPM of participant ' + str(participant_num_input) + ' in ride ' + str(ride_input) + ', by scenario')
#     plt.xlabel('Scenario')
#     plt.ylabel('AVG BPM')
#     plt.show()


# def plot2(participants_input, ride_input, table):
#     print("starting draw_plot2")
#     for line_par in participants_input:
#         x2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['Scenario']]
#         print("x2 =" + str(x2))
#         y2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['RMSSD']]
#         print("y2 =" + str(y2))
#         # plt.plot(x2, y2, color='k', marker='.', label='participant'+str(line_par))
#         plt.plot(x2, y2, label='participant' + str(line_par))
#     plt.title('RMSSD of participants ' + str(participants_input) + ' in ride ' + str(ride_input) + ', by scenario')
#     plt.xlabel('Scenario')
#     plt.ylabel('RMSSD')
#     plt.legend()  # מקרא
#     plt.style.use('fivethirtyeight')
#     plt.show()


def plot_HR_with_scenarios(axis_x_scenarios_input, participant_num_input, parameter,
                           table):  # בלי נסיעות (כלומר כולן נבחרות)
    print("starting draw_plot_HR")
    list_participants = [[] for i in range(
        len(participant_num_input))]  # רשימה של רשימות - כל תא מכיל רשימה שמייצגת את הערכים של כל עמודה עבור כל ערך בציר האיקס
    # example: [**particpant 1: [ scenario 1 value, scenario 2 value .....] **participant 2: [ scenario 1 value, .....]]
    print(list_participants)
    for i in range(len(participant_num_input)):  # לולאה לעמודות (מספר העמודות עבור כל ערך של ציר האיקס)
        print("current line_par is: " + str(participant_num_input[i]))
        for line_sc in axis_x_scenarios_input:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
            print("current line_sc is: " + str(line_sc))
            list_participants[i].append(
                table.loc[(table['Participant'] == participant_num_input[i]) & (table['Scenario'] == line_sc), [
                    parameter]].get(parameter).values[0])  # מכניס לרשימה1 את כל האקג של תרחיש 1 עבור נבדק 3
            # y = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par) & (table['Scenario'] == line_sc), ['Average BPM']]
            # print("current y value is: " + str(y))
    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    bar_width = 1 / (len(participant_num_input) + 1)
    x_chart_width = 1 / len(participant_num_input)
    fig = plt.subplots(figsize=(12, 8))
    br_list = []
    br1 = np.arange((len(axis_x_scenarios_input)))
    for i in range(len(participant_num_input)):
        br1 = [x + bar_width for x in br1]
        br_list.append(br1)
    print("br: " + str(br_list))
    print("par: " + str(list_participants))
    colors = ['r', 'b', 'g', 'y', 'p']
    for i in range(len(list_participants)):
        plt.bar(br_list[i], list_participants[i], color=colors[i], width=bar_width,
                edgecolor='grey', label='PAR' + str(participant_num_input[i]))
    plt.xlabel('Scenario', fontweight='bold', fontsize=15)
    plt.ylabel(parameter, fontweight='bold', fontsize=15)
    plt.xticks([r + x_chart_width for r in range(len(axis_x_scenarios_input))],
               axis_x_scenarios_input)
    plt.legend()
    plt.show()

    # X = np.arange(len(axis_x_scenarios_input))
    # fig = plt.figure()
    # ax = fig.add_axes([0, 0, 1, 1])
    # ax.bar(X + 0.00, list_scenarios[0][0], color='b', width=0.25)
    # ax.bar(X + 0.25, list_scenarios[1][0], color='g', width=0.25)
    # ax.bar(X + 0.50, list_scenarios[2][0], color='r', width=0.25)
    # ax.bar(X + 0.75, list_scenarios[3][0], color='r', width=0.25)
    # ax.bar(X + 1, list_scenarios[4][0], color='r', width=0.25)
    # ax.bar(X + 1.25, list_scenarios[5][0], color='r', width=0.25)
    # ax.bar(X + 1.50, list_scenarios[6][0], color='r', width=0.25)

    # x = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Scenario']]
    # print(x)
    # y = table.loc[
    #     (table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Average BPM']]
    # print(y)
    # plt.plot(x, y, marker='.')
    # plt.title('AVG BPM of participant ' + str(participant_num_input) + ' in ride ' + str(ride_input) + ', by scenario')
    # plt.xlabel('Scenario')
    # plt.ylabel('AVG BPM')
    # plt.show()


def plot_HR_rides(participant_num_input, ride_input, parameter,
                  table):  # מראה עבור כל נסיעה את המשתתפים בעמודות ואקג ממוצע
    print("starting draw_plot_HR_rides")
    list_participants = [[] for i in range(
        len(participant_num_input))]  # רשימה של רשימות - כל תא מכיל רשימה שמייצגת את הערכים של כל עמודה עבור כל ערך בציר האיקס
    # example: [**participant 1: [ ride 1 avg value, ride 2 avg value .....] **participant 2: [ ride 1 avg value, .....]]
    print(list_participants)
    for i in range(len(participant_num_input)):  # לולאה לעמודות (מספר העמודות עבור כל ערך של ציר האיקס)
        print("current line_par is: " + str(participant_num_input[i]))
        for line_r in ride_input:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
            print("current line_r is: " + str(line_r))
            list_participants[i].append(np.average(table.loc[(table['Ride Number'] == line_r) & (
                    table['Participant'] == participant_num_input[i]) & (table[parameter] != 0), [parameter]].get(
                parameter)))  # מכניס לרשימה1 את כל האקג של תרחיש 1 עבור נבדק 3
        # list_participants[i].append((table.loc[(table['Participant'] == participant_num_input[i]), ['Baseline BPM']].get('Baseline BPM').values[0]))#הוספת הבייסלין לרשימה
        print("list_participants:")
        print(list_participants)
    draw_all_graphs(participant_num_input, list_participants, ride_input, 'Rides', parameter, 'Participant')
    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    # bar_width = 1 / (len(participant_num_input) + 1)
    # x_chart_width = 1 / len(participant_num_input)
    # fig = plt.subplots(figsize=(12, 8))
    # br_list = []
    # br1 = np.arange((len(ride_input)))
    # for i in range(len(participant_num_input)):
    #     br1 = [x + bar_width for x in br1]
    #     br_list.append(br1)
    # print("br: " + str(br_list))
    # print("par: " + str(list_participants))
    # colors = ['r','b','g','y','p']
    # for i in range(len(list_participants)):
    #     plt.bar(br_list[i], list_participants[i], color=colors[i], width=bar_width,
    #             edgecolor='grey', label='PAR' + str(participant_num_input[i]))
    # plt.xlabel('Rides', fontweight='bold', fontsize=15)
    # plt.ylabel('Average BPM', fontweight='bold', fontsize=15)
    # plt.xticks([r + x_chart_width for r in range(len(ride_input))],
    #            ride_input)
    # plt.legend()
    # plt.show()


def plot_HR_groups_scenarios(axis_x_scenarios_input, group_num, parameter, table):
    print("starting draw_plot_HR_groups_scenarios")
    list_groups = [[] for i in range(
        (group_num))]  # רשימה של רשימות - כל תא מכיל רשימה שמייצגת את הערכים של כל עמודה עבור כל ערך בציר האיקס
    # example: [**group 1: [ scenario 1 value, scenario 2 value .....] **group 2: [ scenario 1 value, .....]]
    print(list_groups)
    for i in range(group_num):  # לולאה לעמודות (מספר העמודות עבור כל ערך של ציר האיקס)
        print("current line_group is: " + str(i + 1))
        for line_sc in axis_x_scenarios_input:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
            print("current line_sc is: " + str(line_sc))
            list_groups[i].append(np.average(
                table.loc[(table['Scenario'] == line_sc) & (table[parameter] != 0) & (table['Group'] == i + 1), [
                    parameter]].get(parameter)))  # מכניס לרשימה1 את כל האקג של תרחיש 1 עבור נבדק 3
    print(list_groups)
    groups_values_input = list(range(1, group_num + 1))
    # y = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par) & (table['Scenario'] == line_sc), ['Average BPM']]
    # print("current y value is: " + str(y))
    draw_all_graphs(groups_values_input, list_groups, axis_x_scenarios_input, 'Scenario', parameter, 'Group')
    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    # bar_width = 1 / (len(list_groups) + 1)
    # x_chart_width = 1 / len(list_groups)
    # fig = plt.subplots(figsize=(12, 8))
    # br_list = []
    # br1 = np.arange((len(axis_x_scenarios_input)))
    # for i in range(len(list_groups)):
    #     br1 = [x + bar_width for x in br1]
    #     br_list.append(br1)
    # print("br: " + str(br_list))
    # print("par: " + str(list_groups))
    # colors = ['r','b','g','y','p']
    # for i in range(len(list_groups)):
    #     plt.bar(br_list[i], list_groups[i], color=colors[i], width=bar_width,
    #             edgecolor='grey', label='Group' + str(i+1))
    # plt.xlabel('Scenario', fontweight='bold', fontsize=15)
    # plt.ylabel('Average BPM', fontweight='bold', fontsize=15)
    # plt.xticks([r + x_chart_width for r in range(len(axis_x_scenarios_input))],
    #            axis_x_scenarios_input)
    # plt.legend()
    # plt.show()


def plot_HR_groups_rides(group_num, ride_input, parameter, table):
    print("starting draw_plot_HR_groups_rides")
    list_groups = [[] for i in range(
        (group_num))]  # רשימה של רשימות - כל תא מכיל רשימה שמייצגת את הערכים של כל עמודה עבור כל ערך בציר האיקס
    # example: [**group 1: [ ride 1 value, ride 2 value .....] **group 2: [ ride 1 value, .....]]
    print(list_groups)
    for i in range(group_num):  # לולאה לעמודות (מספר העמודות עבור כל ערך של ציר האיקס)
        print("current line_group is: " + str(i + 1))
        for line_r in ride_input:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
            print("current line_sc is: " + str(line_r))
            list_groups[i].append(np.average(
                table.loc[(table['Ride Number'] == line_r) & (table['Group'] == i + 1) & (table[parameter] != 0), [
                    parameter]].get(parameter)))  # מכניס לרשימה1 את כל האקג של קבוצה 1 עבור נסיעה 1
    print(list_groups)
    groups_values_input = list(range(1, group_num + 1))
    print(groups_values_input)
    draw_all_graphs(groups_values_input, list_groups, ride_input, 'Rides', parameter, 'Group')
    # y = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par) & (table['Scenario'] == line_sc), ['Average BPM']]
    # print("current y value is: " + str(y))
    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    # bar_width = 1 / (len(list_groups) + 1)
    # x_chart_width = 1 / len(list_groups)
    # fig = plt.subplots(figsize=(12, 8))
    # br_list = []
    # br1 = np.arange((len(ride_input)))
    # for i in range(len(list_groups)):
    #     br1 = [x + bar_width for x in br1]
    #     br_list.append(br1)
    # print("br: " + str(br_list))
    # print("par: " + str(list_groups))
    # colors = ['r','b','g','y','p']
    # for i in range(len(list_groups)):
    #     plt.bar(br_list[i], list_groups[i], color=colors[i], width=bar_width,
    #             edgecolor='grey', label='Group' + str(groups_values_input[i]))
    # plt.xlabel('Rides', fontweight='bold', fontsize=15)
    # plt.ylabel('Average BPM', fontweight='bold', fontsize=15)
    # plt.xticks([r + x_chart_width for r in range(len(ride_input))],
    #            ride_input)
    # plt.legend()
    # plt.show()


def plot_HR_with_scenarios_all_rides(axis_x_scenarios_input, ride_input, parameter,
                                     table):  # על כל הנסיעות וכל המשתתפים
    ###############לא מוכן###############
    print("starting draw_plot_HR_all_par$rides_with_scenarios")
    list_scenarios_all_par = [[] for i in range(
        len(axis_x_scenarios_input))]  # רשימה של רשימות כמספר התרחישים שנבחרו - כל תא מכיל רשימה שמייצגת את הערכים של כל המשתתפים עבור כל תרחיש בציר האיקס
    # example: [**scenario 1: [ par 1 value, par 2 value .....] **scenario 2: [ par 1 value, .....]]
    print(list_scenarios_all_par)
    i = 0
    for line_sc in axis_x_scenarios_input:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
        print("current line_sc is: " + str(line_sc))
        list_scenarios_all_par[i].append(np.average(
            table.loc[(table['Scenario'] == line_sc) & (table[parameter] != 0), [parameter]].get(
                parameter)))  # מכניס לרשימה1 את כל האקג של תרחיש 1 עבור נבדק 3
    print(list_scenarios_all_par)

    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    bar_width = 1 / 2
    x_chart_width = 1
    fig = plt.subplots(figsize=(12, 8))
    br_list = []
    br1 = np.arange((len(axis_x_scenarios_input)))
    for i in range(len(list_scenarios_all_par)):
        br1 = [x + bar_width for x in br1]
        br_list.append(br1)
    print("br: " + str(br_list))
    print("par: " + str(list_scenarios_all_par))
    colors = ['r', 'b', 'g', 'y', 'p']
    for i in range(len(list_scenarios_all_par)):
        plt.bar(br_list[i], list_scenarios_all_par[i], color=colors[i], width=bar_width,
                edgecolor='grey', label='All Participants')
    plt.xlabel('Scenario', fontweight='bold', fontsize=15)
    plt.ylabel(parameter, fontweight='bold', fontsize=15)
    plt.xticks([r + x_chart_width for r in range(len(axis_x_scenarios_input))],
               axis_x_scenarios_input)
    plt.legend()
    plt.show()


# def draw_all_graphs_with_groups(list_of_groups, list_of_list_columns, list_axis_x, name_axis_x, name_axis_y, name_column):
# # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
# # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
#     bar_width = 1 / (len(list_of_list_columns) + 1)
#     x_chart_width = 1 / len(list_of_list_columns)
#     fig = plt.subplots(figsize=(12, 8))
#     br_list = []
#     br1 = np.arange((len(list_axis_x)))
#     for i in range(len(list_of_list_columns)):
#         br1 = [x + bar_width for x in br1]
#         br_list.append(br1)
#     print("br: " + str(br_list))
#     print("par: " + str(list_of_list_columns))
#     colors = ['r', 'b', 'g', 'y', 'p']
#     for i in range(len(list_of_list_columns)):
#         plt.bar(br_list[i], list_of_list_columns[i], color=colors[i], width=bar_width,
#                 edgecolor='grey', label=name_column + str(list_of_groups[i]))
#     plt.xlabel(name_axis_x, fontweight='bold', fontsize=15)
#     plt.ylabel(name_axis_y, fontweight='bold', fontsize=15)
#     plt.xticks([r + x_chart_width for r in range(len(list_axis_x))],
#                list_axis_x)
#     plt.legend()
#     plt.show()

def general_graph_avg(scenarios, rides, parameter, table):
    rides_values = [[] for i in range(
        len(rides))]  # רשימה של רשימות כמספר התרחישים שנבחרו - כל תא מכיל רשימה שמייצגת את הערכים של כל המשתתפים עבור כל תרחיש בציר האיקס
    # example: [**scenario 1: [ par 1 value, par 2 value .....] **scenario 2: [ par 1 value, .....]]
    # print(list_scenarios_all_par)

    i = 0
    for ride in rides:  # לולאה לערך עבור כל עמודה - מספר הערכים בציר האיקס
        for line_sc in scenarios:
            print("current line_sc is: " + str(line_sc))
            rides_values[i].append(np.average(
                table.loc[(table['Scenario'] == line_sc) & (table[parameter] != 0) & (table['Ride Number'] == ride), [
                    parameter]].get(
                    parameter)))  # מכניס לרשימה1 את כל האקג של תרחיש 1 עבור נבדק 3
        i += 1
    draw_all_graphs(rides, rides_values, scenarios, "Scenarios", parameter, "Ride ")


def draw_all_graphs(list_of_columns_input, list_of_list_columns, list_axis_x, name_axis_x, name_axis_y, name_column):
    # -------------------------ציור הגרף, לא משתנה בין הגרפים, משתנים רק הערכים---------------------
    # ------------- לעשות בפונקציה שמקבלת רשימה של רשימות עבור הערכים, כמות ערכים לציר האיקס, כמות עמודות עבור כל ערך בציר האיקס, ושמות צירים--------
    bar_width= 1
    x_chart_width = 1
    if len(list_of_columns_input) > 1:
        bar_width = 1 / (len(list_of_columns_input) + 1)
        x_chart_width = 1 / len(list_of_columns_input)
    fig = plt.subplots(figsize=(12, 8))
    br_list = []
    br1 = np.arange((len(list_axis_x)))
    for i in range(len(list_of_columns_input)):
        br1 = [x + bar_width for x in br1]
        br_list.append(br1)
    print("br: " + str(br_list))
    print("par: " + str(list_of_list_columns))
    colors = ['r', 'b', 'g', 'y', 'p']
    for i in range(len(list_of_list_columns)):
        plt.bar(br_list[i], list_of_list_columns[i], color=colors[i], width=bar_width,
                edgecolor='grey', label=name_column + str(list_of_columns_input[i]))
    plt.xlabel(name_axis_x, fontweight='bold', fontsize=15)
    plt.ylabel(name_axis_y, fontweight='bold', fontsize=15)
    plt.xticks([r + x_chart_width for r in range(len(list_axis_x))],
               list_axis_x)
    plt.legend()
    plt.show()


def early_table(filename):
    """
        Function that prepares the table - converts the table to a string,
        round the numbers to one digit in the first four columns,
        adds % in the designated places,
        and converts the table to a list.
        A pickle file is saved to the table here.
    """
    if filename == "summary_table":
        for i in range(len(globals.summary_table.index)):
            for j in globals.header_summary_table[3:len(globals.header_summary_table)]:
                globals.summary_table.at[i, j] = round(globals.summary_table.at[i, j], 4)  # 4 ספרות אחרי הנקודה
        globals.summary_table.to_pickle(filename)  # כאן שמרתי פיקל של הטבלה !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        summary_table_list = globals.summary_table.values.tolist()
        summary_table_int = [list(map(int, x)) for x in summary_table_list]
        for i in range(len(summary_table_list)):
            summary_table_list[i][0] = summary_table_int[i][0]
            summary_table_list[i][1] = summary_table_int[i][1]
            summary_table_list[i][2] = summary_table_int[i][2]
            summary_table_list[i][3] = summary_table_int[i][3]
        summary_table_list = [list(map(str, x)) for x in summary_table_list]  # make str list
        return summary_table_list
    else:
        globals.data_quality_table.to_pickle(filename)  # כאן שמרתי פיקל של הטבלה !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        dq_table_list = globals.data_quality_table.values.tolist()
        print(dq_table_list)
        dq_table_int = [list(map(int, x)) for x in dq_table_list]
        for i in range(len(dq_table_list)):
            dq_table_list[i][0] = dq_table_int[i][0]
            dq_table_list[i][1] = dq_table_int[i][1]
            dq_table_list[i][2] = dq_table_int[i][2]
            dq_table_list[i][3] = dq_table_int[i][3]
            dq_table_list[i][9] = str(dq_table_list[i][9]) + ' %'
            dq_table_list[i][15] = str(dq_table_list[i][15]) + ' %'
        dq_table_list = [list(map(str, x)) for x in dq_table_list]  # make str list
        return dq_table_list


def pickle_folders():  # ללא שימוש אפשר למחוק
    """
        The function checks if the pickle folders exist, if not the function creates them.
    """
    list_in_ride = ["ecg pkl", "sim pkl", "rr pkl"]  # רשימת התיקיות לבדיקה
    list_in_base = ["base ecg pkl", "base rr pkl"]  # רשימת התיקיות לבדיקה

    for ride in range(1, globals.par_ride_num + 1):  # מעבר על התיקיות של הנסיעות
        for folder in range(0, len(list_in_ride)):  # rr,ecg, sim
            if not os.path.isdir(globals.main_path + "\\" + "ride " + str(ride) + "\\" + list_in_ride[folder]):
                os.makedirs(globals.main_path + "\\" + "ride " + str(ride) + "\\" + list_in_ride[folder])
                # create folder if not exist
    for folder in range(0, len(list_in_base)):  # base rr, base ecg
        if not os.path.isdir(globals.main_path + "\\" + "base" + "\\" + list_in_base[folder]):
            os.makedirs(globals.main_path + "\\" + "base" + "\\" + list_in_base[folder])
            # create folder if not exist


def checkFolders_of_rides(load_list, values):
    flag = True
    message = "Missing folders:"
    for ride in range(1, globals.par_ride_num + 1):  # מעבר על התיקיות של הנסיעות
        for folder in range(0, len(load_list)):  # rr,ecg, sim
            if not os.path.isdir(values["-MAIN FOLDER-"] + "\\" + "ride " + str(ride) + "\\" + load_list[folder]):
                flag = False
                message += " " + "ride " + str(ride) + "\\" + load_list[folder] + " "
    if not flag:
        sg.popup_quick_message(message, font=("Century Gothic", 14),
                               background_color='red', location=(970, 880), auto_close_duration=5)
    return flag


def checkFolders_of_base(load_list, values):
    flag = True
    message = "Missing folders:"
    for folder in range(0, len(load_list)):  # base rr, base ecg
        if not os.path.isdir(values["-MAIN FOLDER-"] + "\\" + "base" + "\\" + load_list[folder]):
            flag = False
            message += " " + "base" + "\\" + load_list[folder] + " "
    if not flag:
        sg.popup_quick_message(message, font=("Century Gothic", 14),
                               background_color='red', location=(970, 880), auto_close_duration=5)
    return flag


def checkFiles_of_rides(load_list, values):
    message = "Each folder should have EXACTLY " + str(
        len(globals.list_of_existing_par)) + " FILES according to the number of existing participants"
    for ride in range(1, globals.par_ride_num + 1):
        for folder in range(0, len(load_list)):  # ecg, sim, rr
            if len(os.listdir(
                    values["-MAIN FOLDER-"] + "\\" + "ride " + str(ride) + "\\" + load_list[
                        folder])) != len(globals.list_of_existing_par):
                sg.popup_quick_message(message, font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880), auto_close_duration=5)
                return False
            else:  # יש לי מספר קבצים כנדרש בתיקיה
                i = 0
                for file in os.listdir(values["-MAIN FOLDER-"] + "\\" + "ride " + str(ride) + "\\" + load_list[folder]):
                    if str(globals.list_of_existing_par[
                               i]) not in file:  # שולפת קובץ בתיקיה ובודקת אם השם שלו תואם לרשימת הנבדקים הקיימים
                        message = "the file of par " + str(globals.list_of_existing_par[i]) + " of folder " + load_list[
                            folder] + " in ride " + str(ride) + " doesnt exist"
                        sg.popup_quick_message(message, font=("Century Gothic", 14),
                                               background_color='red', location=(970, 880), auto_close_duration=5)
                        return False
                    i += 1
    return True


def checkFiles_of_base(load_list, values):
    message = "Missing files! Each folder should have EXACTLY " + str(
        len(globals.list_of_existing_par)) + " FILES according to the number of existing participants"
    for folder in range(0, len(load_list)):  # base rr, bese ecg
        if len(os.listdir(values["-MAIN FOLDER-"] + "\\" + "base" + "\\" + load_list[folder])) != len(
                globals.list_of_existing_par):
            sg.popup_quick_message(message, font=("Century Gothic", 14),
                                   background_color='red', location=(970, 880), auto_close_duration=5)
            return False
        else:  # יש לי מספר קבצים כנדרש בתיקיה
            i = 0
            for file in os.listdir(values["-MAIN FOLDER-"] + "\\" + "base" + "\\" + load_list[folder]):
                if str(globals.list_of_existing_par[
                           i]) not in file:  # שולפת קובץ בתיקיה ובודקת אם השם שלו תואם לרשימת הנבדקים הקיימים
                    message = "the file of par " + str(globals.list_of_existing_par[i]) + " of folder " + load_list[
                        folder] + " in base doesnt exist"
                    sg.popup_quick_message(message, font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880), auto_close_duration=5)
                    return False
                i += 1
    return True


def exportEXCEL_summary(values):
    """
        The function exports the summary table to Excel according to the columns selected for export.
    """
    path = sg.popup_get_folder(no_window=True, message="choose folder")
    headerlist = [True, True, True, globals.group_num != 0, values['Average BPM'], values['RMSSD'],
                  values['SDSD'], values['SDNN'], values['pNN50'],
                  values['Average BPM'] and values['Baseline'], values['Average BPM'] and values['Baseline'],
                  values['RMSSD'] and values['Baseline'], values['RMSSD'] and values['Baseline'],
                  values['SDNN'] and values['Baseline'], values['SDNN'] and values['Baseline'],
                  values['SDSD'] and values['Baseline'], values['SDSD'] and values['Baseline'],
                  values['pNN50'] and values['Baseline'], values['pNN50'] and values['Baseline']]
    if path:
        # לא ניתן לייצא לאקסל עם עמודות חסרות לכן קודם נייצא לCSV ואז את אותו קובץ נייצא לאקסל
        globals.summary_table.to_csv(path + '\\summary_table.csv', index=False, header=True,
                                     columns=headerlist)  # ייצוא לCSV בהתאם לעמודות שנבחרו לייצוא
        table = pandas.read_csv(path + '\\summary_table.csv')  # קריאה מאותו קובץ
        os.remove(path + '\\summary_table.csv')  # מחיקה של הקובץ
        table.to_excel(path + '\\summary_table.xlsx', index=False)  # ייצוא לאקסל
        sg.popup_quick_message('Exported successfully!', font=("Century Gothic", 10),
                               background_color='white', text_color='black',
                               location=(120, 540))


def exportEXCEL_dq():
    """
        The function exports the DQ table to Excel.
        The function exports the group column only if the subjects were divided into groups.
    """
    path = sg.popup_get_folder(no_window=True, message="choose folder")
    headerlist = [True, True, True, globals.group_num != 0, True, True, True, True, True, True,
                  True, True, True, True, True, True, True, True, True]
    if path:
        # לא ניתן לייצא לאקסל עם עמודות חסרות לכן קודם נייצא לCSV ואז את אותו קובץ נייצא לאקסל
        globals.data_quality_table.to_csv(path + '\\data_quality_table.csv', index=False, header=True,
                                          columns=headerlist)  # ייצוא לCSV בהתאם לעמודות שנבחרו לייצוא
        table = pandas.read_csv(path + '\\data_quality_table.csv')  # קריאה מאותו קובץ
        os.remove(path + '\\data_quality_table.csv')  # מחיקה של הקובץ
        table.to_excel(path + '\\data_quality_table.xlsx', index=False)  # ייצוא לאקסל
        sg.popup_quick_message('Exported successfully!', font=("Century Gothic", 12),
                               background_color='white', text_color='black',
                               location=(1280, 880))


def checks_boundaries(lower, upper):
    if lower >= upper:
        return False
    else:
        return True


def add_files_in_folder(parent, dirname, tree):
    """
        A recursive function that puts into the tree
        the hierarchy of the contents of the selected main folder (the folders and files).
    """
    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
            tree.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname, tree)
        else:
            tree.Insert(parent, fullname, f, values=[], icon=file_icon)


def initial_tree(element, label):
    """
        A function that initializes the tree,
        initializes the tree with each folder selection.
    """
    widget = element.QT_QTreeWidget
    widget.setHeaderLabel(label)  # עדכון שם התיקיה בעץ
    widget.clear()  # מחיקת היסטוריית העץ


def all_input_0_9(event, open_window, values):
    """
        A function that verifies that the values entered in the text boxes are only digits between 0 and 9.
    """
    if event == 'par_num' and values['par_num'] and values['par_num'][-1] not in '0123456789':
        open_window['par_num'].update(values['par_num'][:-1])
    if event == 'scenario_num' and values['scenario_num'] and values['scenario_num'][-1] not in '0123456789':
        open_window['scenario_num'].update(values['scenario_num'][:-1])
    if event == 'scenario_col_num' and values['scenario_col_num'] and values['scenario_col_num'][
        -1] not in '0123456789':
        open_window['scenario_col_num'].update(values['scenario_col_num'][:-1])
    if event == 'sim_sync_time' and values['sim_sync_time'] and values['sim_sync_time'][-1] not in '0123456789.':
        open_window['sim_sync_time'].update(values['sim_sync_time'][:-1])
    if event == 'biopac_sync_time' and values['biopac_sync_time'] and values['biopac_sync_time'][
        -1] not in '0123456789.':
        open_window['biopac_sync_time'].update(values['biopac_sync_time'][:-1])


def sync_handle(open_window, values):
    """
        A function that handles synchronization - disabled and resets the values
        if the user selects that there is synchronization.
    """
    if not values['Sync']:
        open_window["sim_sync_time"].update(disabled=False)
        open_window["biopac_sync_time"].update(disabled=False)
    else:
        open_window["sim_sync_time"].update(disabled=True)
        open_window["sim_sync_time"].update("0")
        open_window["biopac_sync_time"].update(disabled=True)
        open_window["biopac_sync_time"].update("0")


def create_empty_folders():
    """
        A function that creates empty folders according to the format
        and according to the number of trips entered as input.
        If there is already a "main folder" in the path the function deletes it and creates an empty new one.
    """
    path = sg.popup_get_folder(no_window=True, message="choose folder")

    if path:
        if os.path.exists(path + "\\main folder"):
            shutil.rmtree(path + "\\main folder")
        os.makedirs(path + "\\main folder\\base\\base ecg")
        os.makedirs(path + "\\main folder\\base\\base rr")
        for ride in range(1, globals.par_ride_num + 1):
            os.makedirs(path + "\\main folder\\ride " + str(ride) + "\\ecg")
            os.makedirs(path + "\\main folder\\ride " + str(ride) + "\\sim")
            os.makedirs(path + "\\main folder\\ride " + str(ride) + "\\rr")
        sg.popup_quick_message('Created successfully!', font=("Century Gothic", 12),
                               background_color='white', text_color='black',
                               location=(850, 920))
        path = os.path.realpath(path + "\\main folder")
        os.startfile(path)


def tree_handle(path_load_window, values2):
    """
        A function that updates the tree if a new folder is selected.
    """
    if values2["-MAIN FOLDER-"]:  # רק אם הוכנס נתיב והוא לא ריק
        initial_tree(path_load_window['-TREE-'], os.path.basename(values2["-MAIN FOLDER-"]))
        tree = sg.TreeData()
        add_files_in_folder('', values2["-MAIN FOLDER-"], tree)
        path_load_window['-TREE-'].update(tree)  # הצגת תכולת התיקייה שנבחרה


def exceptions_checkbox_handle(event8, exceptions_values_window, values8):
    """
        A function that handles the exceptions checkbox selections.
    """
    if event8 == "checkbox exceptions BPM" or event8 == "checkbox exceptions RR":
        if values8["checkbox exceptions BPM"] or values8["no filtering checkbox"]:
            exceptions_values_window["no filtering checkbox"].update(False)
        if not values8["checkbox exceptions RR"] and not values8["checkbox exceptions BPM"]:
            exceptions_values_window["no filtering checkbox"].update(True)
    if event8 == "no filtering checkbox":
        if values8["no filtering checkbox"]:
            if values8["checkbox exceptions RR"] or values8["checkbox exceptions BPM"]:
                exceptions_values_window["no filtering checkbox"].update(False)
            exceptions_values_window["checkbox exceptions RR"].update(False)
            exceptions_values_window["checkbox exceptions BPM"].update(False)
        if not values8["checkbox exceptions RR"] and not values8["checkbox exceptions BPM"]:
            exceptions_values_window["no filtering checkbox"].update(True)

    if values8["checkbox exceptions RR"]:
        exceptions_values_window.element('_SPIN_RR_LOWER').update(disabled=False)
        exceptions_values_window.element('_SPIN_RR_UPPER').update(disabled=False)
    else:
        exceptions_values_window.element('_SPIN_RR_LOWER').update(disabled=True)
        exceptions_values_window.element('_SPIN_RR_UPPER').update(disabled=True)

    if values8["checkbox exceptions BPM"]:
        exceptions_values_window.element('_SPIN_BPM_LOWER').update(disabled=False)
        exceptions_values_window.element('_SPIN_BPM_UPPER').update(disabled=False)
    else:
        exceptions_values_window.element('_SPIN_BPM_LOWER').update(disabled=True)
        exceptions_values_window.element('_SPIN_BPM_UPPER').update(disabled=True)


def save_input_open_window(values):
    """
        A function that stores the values entered as input to the global values.
    """
    globals.par_num = int(values['par_num'])
    globals.par_ride_num = int(values['par_ride_num'])
    globals.scenario_num = int(values['scenario_num'])
    globals.scenario_col_num = int(values['scenario_col_num'])
    globals.sim_sync_time = float(values['sim_sync_time'])
    globals.biopac_sync_time = float(values['biopac_sync_time'])


def loading_window_update(loading_window, start_time):
    """
        A function that updates all the values on the loading screen.
    """
    loading_window.element("num of num").update(
        "   participants:  " + str(globals.current_par) + " of " + str(len(globals.list_of_existing_par)))
    if globals.percent * 100 < 99.9:
        loading_window.element("percent").update(str(round(globals.percent * 100, 1)) + " %")
        loading_window.element("p bar").update_bar(globals.percent * 100)
    else:
        loading_window.element("percent").update("100 %")
        loading_window.element("p bar").update_bar(100)
    elapsed_time = time.time() - start_time
    loading_window.element("Time elapsed").update(
        time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    loading_window.element("current_ride").update(
        "       rides:  " + str(globals.current_ride) + " of " + str(globals.par_ride_num))
