import pandas
import PySimpleGUIQt as sg

scenario_num = 0
scenario_col_num = 0
par_num = 0
par_ride_num = 0
par_not_existing = []
current_par = 0
percent = 0
list_of_existing_par = []
list_count_rmssd = []
list_start_time = []
list_end_time = []
list_min_bpm = []
list_max_bpm = []
list_null_bpm = []
list_completeness_bpm = []
list_median_bpm = []
# path_noam = r"C:\Users\user\PycharmProjects\ProjectGmar\main folder"
# path_sapir = r"C:\Users\sapir\Desktop\project_gmar_path"
main_path = ""
treedata = sg.TreeData()
header_summary_table = ["Participant", "Ride Number", "Scenario", "Average BPM", "RMSSD", "SDSD", "SDNN", "PNN50",
                        "Baseline BPM",
                        "Substraction BPM", "Baseline RMSSD", "Substraction RMSSD", "Baseline SDNN",
                        "Substraction SDNN",
                        "Baseline SDSD", "Substraction SDSD", "Baseline PNN50",
                        "Substraction PNN50"]
summary_table = pandas.DataFrame(columns=header_summary_table)  # create empty table,only with columns names
header_data_quality = ["Participant", "Ride Number", "Scenario", "Start time", "End time",
                       "BPM(ecg) : Total number of rows", "BPM(ecg) : Number of empty rows",
                       "BPM(ecg) : % Completeness", "BPM(ecg) : Minimum value",
                       "BPM(ecg) : Maximum value", "BPM(ecg) : Median",
                       "HRV methods(rr) : Total number of rows",
                       "HRV methods(rr) : Number of empty rows",
                       "HRV methods(rr) : % Completeness",
                       "HRV methods(rr) : Minimum value",
                       "HRV methods(rr) : Maximum value", "HRV methods(rr) : Median"]
data_quality_table = pandas.DataFrame(columns=header_data_quality)

"""
def initialize():
    global scenario_num
    global scenario_col_num
    global par_num
    global par_ride_num
    global current_par
    global main_path
    global percent
    global list_count_rmssd  # list which contains the number of N (RR intervals) in all scenarios.
    global summary_table
    global data_quality_table
    global header_summary_table
    global header_data_quality
    global treedata
    global fig  # ???????????????
    # global participant_num_input
"""
