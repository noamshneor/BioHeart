from enum import Enum
import pandas
import PySimpleGUIQt as sg


class Filter(Enum):
    NONE = 1
    BPM = 2
    RR = 3
    BOTH = 4


filter_type = Filter.NONE  # ??????????????????????????????????????????????????

scenario_num = 0  # Number of scenarios (input)
scenario_col_num = 0  # Scenario column number in the simulator file (input)
par_num = 0  # Total number of participants (input)
par_ride_num = 0  # Number of rides each participant went through (input)
par_not_existing = []  # List of participants excluded from the experiment (input)
list_of_existing_par = []  # List of participants left after deleting the excluded subjects
group_num = 0  # Number of groups in the experiment (input)
lists_of_groups = []  # (input) The list of subjects is associated with groups, in each index a different group: 0=group1, 1=group2....
main_path = ""  # The path of the main folder (input)

sim_sync_time = 0.0  # Number of seconds for synchronization (input)
biopac_sync_time = 0.0  # Number of seconds for synchronization (input)
current_par = 0  # Stores the current participant on which processing is performed
current_ride = 0  # Stores the current ride on which processing is performed
percent = 0  # Stores processing and loading percentages

is_pkl = True  # ??????????????????????????????????????????????????

scenarios_list = []  # list of scenarios for Graph window
rides_list = []  # list of rides for Graph window
list_count_rr_intervals_flag = []  # Number of RR intervals per scenario
list_start_time = []  # List of start times of each scenario - for DataQuality table
list_end_time = []  # List of end times of each scenario - for DataQuality table
list_min_bpm = []  # List of min value of each scenario (ECG) - for DataQuality table
list_max_bpm = []  # List of max value of each scenario (ECG) - for DataQuality table
list_null_bpm = []  # List of null value of each scenario (ECG) - for DataQuality table
list_completeness_bpm = []  # List of completeness (%) of each scenario (ECG) - for DataQuality table
list_median_bpm = []  # List of medians of each scenario (ECG) - for DataQuality table
list_min_rr = []  # List of min value of each scenario (RR) - for DataQuality table
list_max_rr = []  # List of max value of each scenario (RR) - for DataQuality table
list_null_rr = []  # List of null value of each scenario (RR) - for DataQuality table
list_completeness_rr = []  # List of completeness (%) of each scenario (RR) - for DataQuality table
list_median_rr = []  # List of medians of each scenario (RR) - for DataQuality table

RR_lower = 0  # RR lower range - for exceptional screening (input)
RR_upper = 0  # RR upper range - for exceptional screening (input)
BPM_lower = 0  # BPM lower range - for exceptional screening (input)
BPM_upper = 0  # BPM upper range - for exceptional screening (input)


header_summary_table = ["Participant", "Ride Number", "Scenario", "Group", "Average BPM", "RMSSD", "SDSD", "SDNN", "PNN50",
                        "Baseline BPM",
                        "Subtraction BPM", "Baseline RMSSD", "Subtraction RMSSD", "Baseline SDNN",
                        "Subtraction SDNN",
                        "Baseline SDSD", "Subtraction SDSD", "Baseline PNN50",
                        "Subtraction PNN50"]
summary_table = pandas.DataFrame(columns=header_summary_table)  # create empty table,only with columns names

header_data_quality = ["Participant", "Ride Number", "Scenario", "Group", "Start time (sec)", "End time (sec)", "Duration (sec)",
                       "BPM(ecg) : Total number of rows", "BPM(ecg) : Number of empty rows",
                       "BPM(ecg) : % Completeness", "BPM(ecg) : Minimum value",
                       "BPM(ecg) : Maximum value", "BPM(ecg) : Median",
                       "HRV methods(rr) : Total number of rows",
                       "HRV methods(rr) : Number of empty rows",
                       "HRV methods(rr) : % Completeness",
                       "HRV methods(rr) : Minimum value",
                       "HRV methods(rr) : Maximum value", "HRV methods(rr) : Median"]
data_quality_table = pandas.DataFrame(columns=header_data_quality)  # create empty table,only with columns names

methods_list = ["Average BPM", "RMSSD", "SDSD", "SDNN", "PNN50", "Subtraction BPM",
                "Subtraction RMSSD", "Subtraction SDNN",
                "Subtraction SDSD", "Subtraction PNN50"]

