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
    global header
    global treedata
    global fig#???????????????
    #global participant_num_input
    scenario_num = 7
    scenario_col_num = 11
    par_num = 2
    par_ride_num = 2
    current_par = 0
    percent = 0
    list_count_rmssd = [0] * (scenario_num + 1)
    main_path = r"C:\Users\sapir\Desktop\project_gmar_path_newFolders"# לבדוקק למה חייב את זה, ולא כקלט מהמשתמש