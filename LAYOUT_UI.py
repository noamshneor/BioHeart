import PySimpleGUIQt as sg

import globals


def graphs_window_layout():
    # global par_num
    # global par_ride_num
    participants_list = list(range(1, globals.par_num + 1))
    rides_list = list(range(1, globals.par_ride_num + 1))
    layout_graphs_window = \
        [
            [
                sg.Column(layout=[
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
                        sg.Radio(group_id="GRAPH", text="   AVG BPM for specific participant",
                                 background_color="transparent",
                                 key='avg bpm 1 par', size_px=(670, 35), font=("Century Gothic", 16, 'bold'),
                                 enable_events=True, text_color='red'),
                        # sg.Graph(canvas_size=(400, 400), graph_bottom_left=(-105, -105), graph_top_right=(105, 105),
                        # background_color='white', key='graph', tooltip='This is a cool graph!')
                        # sg.Canvas(size=(200,200), background_color='white',key='-CANVAS-')
                    ],
                    [
                        sg.Text('        participants number:', size=(32, 1), background_color="transparent",
                                visible=False,
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
                        sg.Combo(values=rides_list, size=[50, 25], key='combo_ride_graph1', visible=False,
                                 enable_events=True,
                                 font=("Century Gothic", 12), readonly=True, default_value=""),

                    ],
                    [
                        sg.Text("", background_color="transparent", size=(0, 40)),
                    ],
                    [
                        sg.Radio(group_id="GRAPH", text="  RMSSD of participants", background_color="transparent",
                                 key="rmssd for several par", size=(670, 35), font=("Century Gothic", 16, 'bold'),
                                 enable_events=True,
                                 text_color='red'),
                    ],
                    [
                        sg.Text('        participants number:', size=(32, 1), background_color="transparent",
                                visible=False,
                                key='participant graph2',
                                font=("Century Gothic", 12), text_color='black'),
                        # sg.Input(size=[120, 25], key='combo_par_graph2', visible=False, enable_events=True,
                        # font=("Century Gothic", 12))
                        sg.Listbox(participants_list, size=(10, 2), key='combo_par_graph2', select_mode='multiple',
                                   visible=False, enable_events=True, font=("Century Gothic", 12))

                    ],
                    [
                        sg.Text('        ride number:', size=(32, 1), background_color="transparent", visible=False,
                                key='ride graph2', font=("Century Gothic", 12), text_color='black'),
                        sg.Combo(values=rides_list, size=[50, 25], key='combo_ride_graph2', visible=False,
                                 enable_events=True,
                                 font=("Century Gothic", 12), readonly=True),

                    ],
                    [
                        sg.Text("", background_color="transparent", size=(0, 200)),
                    ],
                    [
                        sg.Button("BACK", size=(150, 45), font=("Century Gothic", 18), key="graphs back",
                                  enable_events=True),
                        sg.Text("", background_color="transparent", size=(80, 35),
                                font=("Century Gothic", 16)),
                        sg.Button("CONTINUE", size=(220, 45), font=("Century Gothic", 18), key="CONTINUE_GRAPH",
                                  enable_events=True)
                    ]
                ], background_color="transparent")
            ]

        ]
    return layout_graphs_window


def data_quality_table_window_layout(dq_table_list):
    layout_data_quality_table_window = \
        [
            [
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(0, 80))],
                    [sg.Table(values=dq_table_list, headings=globals.header_data_quality,
                              auto_size_columns=True, bind_return_key=True,
                              num_rows=18, background_color="white", alternating_row_color="lightblue",
                              enable_events=True, key="DataQTable", font=("Century Gothic", 10),
                              text_color="black", justification='center')],
                    [
                        sg.Text(text="", background_color="transparent", size_px=(700, 50)),
                        sg.Button(button_text="EXPORT", size_px=(150, 60), key="dq export", enable_events=True,
                                  font=("Century Gothic", 16)),
                        sg.Text(text="", background_color="transparent", size_px=(100, 0)),
                        sg.Button(button_text="BACK", size_px=(150, 60), key="dq back", enable_events=True,
                                  font=("Century Gothic", 16))
                    ],
                ], background_color="transparent"
                )
            ]
        ]
    return layout_data_quality_table_window


def summary_table_window_layout(summary_table_list):
    layout_summary_table_window = \
        [
            [
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(0, 140), )],
                    [
                        sg.Checkbox("Average BPM", background_color='transparent', key='Average BPM', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="Average of the number of heart beats per minute (BPM).")
                    ],
                    [
                        sg.Checkbox("RMSSD", background_color='transparent', key='RMSSD', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="The root mean square of successive differences between normal heartbeats (RMSSD) is obtained by first calculating each successive time difference between heartbeats in ms. Then, each of the values is squared and the result is averaged before the square root of the total is obtained.")
                    ],
                    [
                        sg.Checkbox("SDSD", background_color='transparent', key='SDSD', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="The standard deviation of successive RR interval differences (SDSD).")
                    ],
                    [
                        sg.Checkbox("SDNN", background_color='transparent', key='SDNN', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="The standard deviation of the IBI(Inter-Beat Interval) of normal sinus beats (SDNN) is measured in ms.")
                    ],
                    [
                        sg.Checkbox("pNN50", background_color='transparent', key='pNN50', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="The percentage of adjacent NN intervals that differ from each other by more than 50 ms (pNN50).")
                    ],
                    [
                        sg.Checkbox("Baseline BPM", background_color='transparent', key='Baseline BPM', default=True,
                                    enable_events=True, font=("Century Gothic", 13), text_color="black",
                                    tooltip="Resting average beats per minute (BPM).")
                    ],
                    [sg.Text(text="", background_color="transparent", size_px=(0, 60))],
                    [sg.Button(button_text="Export to CSV", size_px=(250, 60), key="Export to CSV",
                               enable_events=True,
                               font=("Century Gothic", 16))]
                ], background_color="transparent"),
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(0, 60))],
                    [sg.Table(values=summary_table_list, headings=globals.header_summary_table,
                              auto_size_columns=True, bind_return_key=True,
                              num_rows=18, background_color="white", alternating_row_color="lightblue",
                              enable_events=True, key="SumTable", font=("Century Gothic", 10),
                              text_color="black", justification='center')],
                    [sg.Text(text="", background_color="transparent", size_px=(100, 100))],
                ], background_color="transparent"
                ),
                sg.Column(layout=[
                    [sg.Text(text="", background_color="transparent", size_px=(200, 250))],
                    [sg.Button(button_text="Data Quality", size_px=(220, 60), key="dq button", enable_events=True,
                               font=("Century Gothic", 16))],
                    [sg.Text(text="", background_color="transparent", size_px=(200, 50))],
                    [sg.Button(button_text="Graphs", size_px=(220, 60), key="Graphs button", enable_events=True,
                               font=("Century Gothic", 16))],
                    [sg.Text(text="", background_color="transparent", size_px=(200, 50))],
                    [sg.Button(button_text="Restart", size_px=(220, 60), key="Restart button", enable_events=True,
                               font=("Century Gothic", 16))],
                    [sg.Text(text="", background_color="transparent", size_px=(200, 50))],
                    [sg.Button(button_text="EXIT", size_px=(220, 60), key="summary exit", enable_events=True,
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
                sg.Text(text="              0 of " + str(globals.par_num), background_color="transparent",
                        text_color='black',
                        size_px=(430, 35), font=("Century Gothic", 20), key="num of num", enable_events=True)
            ],
            [
                sg.Text(text="              ", background_color="transparent", size_px=(100, 35)),
                sg.Text(text="", background_color="transparent", text_color='black',
                        size_px=(350, 60),
                        font=("Century Gothic", 20), key="current_ride", enable_events=True),
            ],
            [
                sg.Text(text="               ", background_color="transparent", size_px=(185, 35)),
                sg.Text(text=str(globals.percent * 100) + " %", background_color="transparent", text_color='black',
                        size_px=(200, 60),
                        font=("Century Gothic", 24), key="percent", enable_events=True),
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 30))
            ],
            [
                sg.Text(text="    Time elapsed:  ", background_color="transparent", text_color='black',
                        size_px=(300, 35), font=("Century Gothic", 16)),
                sg.Text("00:00:00", background_color="transparent", text_color='black', size_px=(150, 35),
                        font=("Century Gothic", 16), key="Time elapsed", enable_events=True)
            ],
            [
                sg.Text(text="", background_color="transparent", size_px=(100, 50))
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
                sg.Tree(data=globals.treedata,
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
                sg.Text("", background_color="transparent", size=(250, 450))
            ],
            [
                sg.Text("                             Participant’s number", background_color="transparent",
                        size=(670, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[80, 40], justification="center", key="par_num", enable_events=True,
                         font=("Century Gothic", 16)),
                sg.Text("          Number of participant’s rides", background_color="transparent",
                        size=(630, 35), font=("Century Gothic", 18), text_color='black'),
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
                         font=("Century Gothic", 16)),
                sg.Text("          Scenario’s column number", background_color="transparent",
                        size=(630, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[80, 40], justification="center", key='scenario_col_num', enable_events=True,
                         font=("Century Gothic", 16))
            ],
            [
                sg.Text("", background_color="transparent", size=(250, 70)),
            ],
            [
                sg.Text("", background_color="transparent", size=(30, 0)),
                sg.Checkbox("Synchronized", background_color='transparent', key='Sync', default=True,
                            enable_events=True, font=("Century Gothic", 18), text_color="black", size_px=(370, 40),
                            tooltip="Did you run the simulator and the ECG measurement at the same time?"),
                sg.Text("Simulator start at", background_color="transparent",
                        size=(310, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[100, 40], justification="center", key="sim_start", enable_events=True,
                         font=("Century Gothic", 16), default_text="0", disabled=True),
                sg.Text(" ,   ", background_color="transparent", size=(50, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Text("ECG start at", background_color="transparent",
                        size=(230, 35), font=("Century Gothic", 18), text_color='black'),
                sg.Input(size=[100, 40], justification="center", key='ecg_start', enable_events=True,
                         font=("Century Gothic", 16), default_text="0", disabled=True),
            ],
            [
                sg.Text("", background_color="transparent", size=(320, 240)),
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
