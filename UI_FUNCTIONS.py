import os

import PySimpleGUIQt as sg
from matplotlib import pyplot as plt

import globals


# --------------------------------------------- UI FUNCTIONS ---------------------------------------------
def draw_plot1(participant_num_input, ride_input, table):
    x = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Scenario']]
    print(x)
    y = table.loc[
        (table['Ride Number'] == ride_input) & (table['Participant'] == participant_num_input), ['Average BPM']]
    print(y)
    plt.plot(x, y, marker='.')
    plt.title('AVG BPM of participant ' + str(participant_num_input) + ' in ride ' + str(ride_input) + ', by scenario')
    plt.xlabel('Scenario')
    plt.ylabel('AVG BPM')
    plt.show()


def draw_plot2(participants_input, ride_input, table):
    for line_par in participants_input:
        x2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['Scenario']]
        y2 = table.loc[(table['Ride Number'] == ride_input) & (table['Participant'] == line_par), ['RMSSD']]
        # plt.plot(x2, y2, color='k', marker='.', label='participant'+str(line_par))
        plt.plot(x2, y2, label='participant' + str(line_par))
    plt.title('RMSSD of participants ' + str(participants_input) + ' in ride ' + str(ride_input) + ', by scenario')
    plt.xlabel('Scenario')
    plt.ylabel('RMSSD')
    plt.legend()  # מקרא
    plt.style.use('fivethirtyeight')
    plt.show()


def early_table(filename):
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
        summary_table_list = [list(map(str, x)) for x in summary_table_list]  # make str list
        return summary_table_list
    else:
        globals.data_quality_table.to_pickle(filename)  # כאן שמרתי פיקל של הטבלה !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        dq_table_list = globals.data_quality_table.values.tolist()
        dq_table_int = [list(map(int, x)) for x in dq_table_list]
        for i in range(len(dq_table_list)):
            dq_table_list[i][0] = dq_table_int[i][0]
            dq_table_list[i][1] = dq_table_int[i][1]
            dq_table_list[i][2] = dq_table_int[i][2]
            dq_table_list[i][7] = str(dq_table_list[i][7]) + ' %'
            dq_table_list[i][13] = str(dq_table_list[i][13]) + ' %'
        dq_table_list = [list(map(str, x)) for x in dq_table_list]  # make str list
        return dq_table_list


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
        for folder in range(0, len(load_list)):#ecg, sim, rr
            if len(os.listdir(
                    values["-MAIN FOLDER-"] + "\\" + "ride " + str(ride) + "\\" + load_list[
                        folder])) != len(globals.list_of_existing_par):
                sg.popup_quick_message(message, font=("Century Gothic", 14),
                                       background_color='red', location=(970, 880), auto_close_duration=5)
                return False
            else:#יש לי מספר קבצים כנדרש בתיקיה
                i=0
                for file in os.listdir(values["-MAIN FOLDER-"] + "\\" + "ride " + str(ride) + "\\" + load_list[folder]):
                    if str(globals.list_of_existing_par[i]) not in file:# שולפת קובץ בתיקיה ובודקת אם השם שלו תואם לרשימת הנבדקים הקיימים
                        message = "the file of par " + str(globals.list_of_existing_par[i]) + " of folder " + load_list[folder] + " in ride " + str(ride) + " doesnt exist"
                        sg.popup_quick_message(message, font=("Century Gothic", 14),
                                               background_color='red', location=(970, 880), auto_close_duration=5)
                        return False
                    i += 1
    return True


def checkFiles_of_base(load_list, values):
    message = "Missing files! Each folder should have EXACTLY " + str(
       len(globals.list_of_existing_par)) + " FILES according to the number of existing participants"
    for folder in range(0, len(load_list)):  # base rr, bese ecg
        if len(os.listdir(values["-MAIN FOLDER-"] + "\\" + "base" + "\\" + load_list[folder])) != len(globals.list_of_existing_par):
            sg.popup_quick_message(message, font=("Century Gothic", 14),
                                   background_color='red', location=(970, 880), auto_close_duration=5)
            return False
        else:  # יש לי מספר קבצים כנדרש בתיקיה
            i = 0
            for file in os.listdir(values["-MAIN FOLDER-"] + "\\" + "base" + "\\" + load_list[folder]):
                if str(globals.list_of_existing_par[i]) not in file:  # שולפת קובץ בתיקיה ובודקת אם השם שלו תואם לרשימת הנבדקים הקיימים
                    message = "the file of par " + str(globals.list_of_existing_par[i]) + " of folder " + load_list[folder] + " in base doesnt exist"
                    sg.popup_quick_message(message, font=("Century Gothic", 14),
                                           background_color='red', location=(970, 880), auto_close_duration=5)
                    return False
                i += 1
    return True


def exportCSV(values):
    headerlist = [True, True, True, values['Average BPM'], values['RMSSD'],
                  values['SDSD'], values['SDNN'], values['pNN50'], values['Baseline BPM'],
                  values['Baseline BPM'], values['RMSSD'], values['RMSSD'], values['SDNN'], values['SDNN'],
                  values['SDSD'], values['SDSD'], values['pNN50'], values['pNN50']]
    globals.summary_table.to_csv('summary_table.csv', index=False, header=True,
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
            globals.treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        else:

            globals.treedata.Insert(parent, fullname, f, values=[], icon=file_icon)