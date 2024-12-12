# -*- coding: utf-8 -*-
# -*- coding: gbk -*-
import csv
import time
import timeit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy
from datetime import datetime
import os


###########################################################################################################
import tkinter as tk
from tkinter import ttk, filedialog

## pip install ttkwidgets
from ttkwidgets.autocomplete import AutocompleteCombobox
column_names = ["VehicleType", "DirectionTime_O", "GantryID_O", "DirectionTime_D", "GantryID_D", "TripLength", "TripEnd", "TripInformation"]

traffic_data = pd.DataFrame(columns=column_names)

##########################################################################################################
################################################  GUI  ###################################################
##########################################################################################################

# 全新版本
def link_start_ultra():
    # 全局变量，用于存储处理好的数据
    processed_data = None
    # 处理函数，输出一个数据集
    def main_part():
        # 若空则初始化
        if timepoint_entry.get() == "":
            timepoint_entry.insert(tk.END, "06:00")
        if bus_entry.get() == "":
            bus_entry.insert(tk.END, "5,31,32,41,42")

        # 获取用户输入的起点站和终点站
        buslist = [int(num) for num in bus_entry.get().split(",")]
        start_station = start_station_entry.get()
        end_station = end_station_entry.get()
        timepoint = timepoint_entry.get()

        filtered1 = traffic_data[traffic_data.loc[:, "VehicleType"].isin(buslist)]
        filtered2 = filtered1[filtered1.loc[:, "TripInformation"].str.contains(start_station)]
        filtered2 = filtered2[filtered2.loc[:, "TripInformation"].str.contains(end_station)]
        pattern = f"(.{{8}})+" + start_station
        extracted_strings = filtered2.loc[:, "TripInformation"].str.extract(pattern, expand=False)
        filtered2["RealTime"] = extracted_strings
        filtered2["Start"] = start_station
        filtered2["End"] = end_station
        sorted_object = filtered2.sort_values(by=["RealTime", "VehicleType"], ascending=True)
        time_obj = datetime.strptime(timepoint, "%H:%M")
        formatted_time = time_obj.strftime("%H:%M:%S")
        filtered3 = sorted_object[sorted_object.loc[:, "RealTime"] > formatted_time]
        result = filtered3.loc[:, ["VehicleType","DirectionTime_O","GantryID_O","TripLength","DirectionTime_D", "GantryID_D", "TripEnd"]]
        return result

    # 全局变量来存储选中的文件夹路径
    selected_folder_path = ""

    def select_folder():
        global selected_folder_path
        selected_folder_path = filedialog.askdirectory(title="选择文件夹")
        if selected_folder_path:
            # 获取文件夹中的所有CSV文件
            csv_files = [f for f in os.listdir(selected_folder_path) if f.endswith('.csv')]
            if csv_files:
                # 更新combobox的选项
                combo_file_list['values'] = csv_files
                combo_file_list.set(csv_files[0])  # 设置默认选择第一个文件
            else:
                print("文件夹中没有CSV文件")
        else:
            print("请选择一个文件夹")

    def load_selected_file():
        global traffic_data
        global selected_folder_path
        if not selected_folder_path:
            print("请先选择一个文件夹")
            return
        selected_file = combo_file_list.get()
        if selected_file:
            file_path = os.path.join(selected_folder_path, selected_file)
            # 读取选中的CSV文件
            selected_file_data = pd.read_csv(file_path, names=column_names)
            # 将数据追加到traffic_data
            traffic_data = selected_file_data
            print(f"成功加载文件：{selected_file}")
            print(traffic_data.head())
            print(len(traffic_data))
            # 重新计算stationlist
            stationlist = np.sort(traffic_data.loc[:, "GantryID_O"].unique()).tolist()
            # 更新combobox的选项
            start_station_entry['values'] = stationlist
            end_station_entry['values'] = stationlist
        else:
            print("请选择一个文件")


    # 全局变量来存储选中的文件夹路径
    selected_folder_path1 = ""

    def select_folder1():
        global selected_folder_path1
        selected_folder_path1 = filedialog.askdirectory(title="选择文件夹")
        if selected_folder_path1:
            # 获取文件夹中的所有CSV文件
            csv_files = [f for f in os.listdir(selected_folder_path1) if f.endswith('.csv')]
            if csv_files:
                # 更新combobox的选项
                combo_file_list1['values'] = csv_files
                combo_file_list1.set(csv_files[0])  # 设置默认选择第一个文件
            else:
                print("文件夹中没有CSV文件")
        else:
            print("请选择一个文件夹")

    def merge_selected_file():
        global traffic_data
        global selected_folder_path1
        if not selected_folder_path1:
            print("请先选择一个文件夹")
            return
        selected_file = combo_file_list1.get()
        if selected_file:
            file_path = os.path.join(selected_folder_path1, selected_file)
            # 读取选中的CSV文件
            selected_file_data = pd.read_csv(file_path, names=column_names)
            # 将数据追加到traffic_data
            traffic_data = pd.concat([traffic_data,selected_file_data])
            print(f"成功加载文件：{selected_file}")
            print(traffic_data.head())
            print(len(traffic_data))
            # 重新计算stationlist
            stationlist = np.sort(traffic_data.loc[:, "GantryID_O"].unique()).tolist()
            # 更新combobox的选项
            start_station_entry['values'] = stationlist
            end_station_entry['values'] = stationlist
        else:
            print("请选择一个文件")

    def export_data():
        global processed_data
        if processed_data is None or processed_data.empty:
            print("Warning: No merged data available to export.")  # 使用 print 替代 messagebox.showwarning
            return

        # 让用户选择保存文件的路径和类型
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
            initialdir=".",
            title="导出处理好的数据"
        )

        if file_path:
            if file_path.endswith('.csv'):
                processed_data.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                processed_data.to_excel(file_path, index=False)
            print(f"Success: Data exported to {file_path}")  # 使用 print 替代 messagebox.showinfo
        else:
            print("未选择导出路径")
    # 输出查询结果
    def search_button_click():
        global processed_data  # 声明全局变量
        result = main_part()
        processed_data = result  # 保存搜索结果
        # 更新结果显示
        # 清空结果显示框
        result_text.delete('1.0', tk.END)
        # 将处理好的数据集输出到结果显示框
        result_text.insert(tk.END, result.to_string(index=False))
        # 设置文本样式和对齐方式
        result_text.tag_configure("center", justify="center")
        result_text.tag_add("center", "1.0", "end")

    # 输出排序结果
    def sort_button_click():
        global processed_data  # 声明全局变量
        result = main_part()
        indi = combo_sort_column.get()
        sorted_result = result.sort_values(by=indi, ascending=True)
        processed_data = sorted_result  # 保存排序结果
        # 更新结果显示
        # 清空结果显示框
        result_text.delete('1.0', tk.END)
        # 将处理好的数据集输出到结果显示框
        result_text.insert(tk.END, sorted_result.to_string(index=False))
        # 设置文本样式和对齐方式
        result_text.tag_configure("center", justify="center")
        result_text.tag_add("center", "1.0", "end")


    # 创建主窗口
    root = tk.Tk()
    root.title("交通数据查询")

    # 设置窗口大小
    root.geometry('1280x750')

    # 标题
    title = tk.Label(root, text='欢迎查询台湾交通数据', font=('思源黑体 CN', 25, 'bold'), width=20, height=3)
    title.pack()

    # 子标题1
    subtitle1 = tk.Label(root, text='导入', font=('思源黑体 CN', 20, 'bold'), width=10, height=2)
    subtitle1.place(x=2, y=50)

    # 创建一个下拉框，显示文件夹中的 CSV 文件
    combo_file_list = ttk.Combobox(root, font=('Arial', 12), width=12)
    combo_file_list.pack(pady=10)
    combo_file_list.place(x=110, y=70)

    select_folder_button = tk.Button(root, text="选择文件夹", command=select_folder, font=('Arial', 8))
    select_folder_button.place(x=260, y=70)

    # 创建加载文件按钮
    load_file_button = tk.Button(root, text="确认", command=load_selected_file, font=('Arial', 8))
    load_file_button.place(x=340, y=70)

    # 子标题2
    subtitle2 = tk.Label(root, text='合并', font=('思源黑体 CN', 20, 'bold'), width=10, height=2)
    subtitle2.place(x=2, y=100)

    # 创建一个下拉框，显示文件夹中的 CSV 文件
    combo_file_list1 = ttk.Combobox(root, font=('Arial', 12), width=12)
    combo_file_list1.pack(pady=10)
    combo_file_list1.place(x=110, y=120)

    select_folder_button1 = tk.Button(root, text="选择文件夹", command=select_folder1, font=('Arial', 8))
    select_folder_button1.place(x=260, y=120)

    # 创建合并文件按钮
    load_file_button1 = tk.Button(root, text="确认", command=merge_selected_file, font=('Arial', 8))
    load_file_button1.place(x=340, y=120)

    # 子标题3
    subtitle3 = tk.Label(root, text='导出', font=('思源黑体 CN', 20, 'bold'), width=10, height=2)
    subtitle3.place(x=2, y=150)

    # 导出数据按钮
    export_button = tk.Button(root, text="导出文件", command=export_data, font=('Arial', 8))
    export_button.place(x=130, y=170)

    # 子标题4
    subtitle4 = tk.Label(root, text='查询', font=('思源黑体 CN', 20, 'bold'), width=10, height=2)
    subtitle4.place(x=2, y=200)

    # 创建公交标签和输入框
    bus_label = tk.Label(root, text="全部车辆: 5,31,32,41,42", font=('思源黑体 CN', 12, 'bold'))
    bus_label.place(x=52, y=255)

    bus_label2 = tk.Label(root, text="车辆类型(格式如:5,31,41):", font=('思源黑体 CN', 15, 'bold'))
    bus_label2.place(x=50, y=275)
    # bus_label.pack()

    bus_entry = tk.Entry(root, font=('思源黑体 CN', 15, 'bold'))
    bus_entry.place(x=55, y=315)
    # bus_entry.pack()

    # 创建起点站标签和输入框
    start_station_label = tk.Label(root, text="上车站:", font=('思源黑体 CN', 15, 'bold'))
    start_station_label.place(x=50, y=355)
    # start_station_label.pack()

    stationlist = np.sort(traffic_data.loc[:, "GantryID_O"].unique()).tolist()
    start_station_entry = AutocompleteCombobox(completevalues=stationlist, font=('思源黑体 CN', 15, 'bold'), width=15,state="readonly")
    # start_station_entry.insert(0, "上车站:")
    start_station_entry.place(x=140, y=358)
    # start_station_entry.pack()

    # 创建终点站标签和输入框
    end_station_label = tk.Label(root, text="目的地:", font=('思源黑体 CN', 15, 'bold'))
    end_station_label.place(x=50, y=385)
    # end_station_label.pack()

    stationlist = np.sort(traffic_data.loc[:, "GantryID_O"].unique()).tolist()
    end_station_entry = AutocompleteCombobox(completevalues=stationlist, font=('思源黑体 CN', 15, 'bold'), width=15,state="readonly")
    # end_station_entry.insert(0, "目的地:")

    end_station_entry.place(x=140, y=398)
    # end_station_entry.pack()

    # 创建时间点标签和输入框
    timepoint_label = tk.Label(root, text="到达起点站时间:", font=('思源黑体 CN', 15, 'bold'))
    timepoint_label.place(x=50, y=440)
    # timepoint_label.pack()

    start_time = "06:00"
    end_time = "22:10"
    interval = 1 # 间隔时间，单位为分钟
    start_hour, start_minute = map(int, start_time.split(":"))
    end_hour, end_minute = map(int, end_time.split(":"))
    start_total_minutes = start_hour * 60 + start_minute
    end_total_minutes = end_hour * 60 + end_minute
    time_list = []
    current_minutes = start_total_minutes
    while current_minutes <= end_total_minutes:
        hour = current_minutes // 60
        minute = current_minutes % 60
        time_str = f"{hour:02d}:{minute:02d}"
        time_list.append(time_str)
        current_minutes += interval

    timepoint_entry = AutocompleteCombobox(completevalues=time_list, font=('思源黑体 CN', 15, 'bold'))
    timepoint_entry.place(x=55, y=480)
    # timepoint_entry.pack()

    # 创建搜索按钮
    search_button = tk.Button(root, text="单击查询", command=search_button_click, font=('思源黑体 CN', 15, 'bold'))
    search_button.place(x=55, y=520)
    # search_button.pack()

    # 创建结果显示框
    result_text = tk.Text(root, height=25, width=72, font=('思源黑体 CN', 15, 'bold'))
    result_text.place(x=410, y=120)
    # result_text.pack()

    # 排序部分的布局
    subtitle2 = tk.Label(root, text='排序', font=('思源黑体 CN', 20, 'bold'), width=10, height=2)
    subtitle2.place(x=2, y=560)

    # 排序列标签和下拉框
    label_sort_column = tk.Label(root, text='排序列:', font=('思源黑体 CN', 15, 'bold'))
    label_sort_column.place(x=50, y=615)

    COLUMN_NAMES = ["VehicleType","DirectionTime_O","GantryID_O", "TripLength"]
    combo_sort_column = AutocompleteCombobox(completevalues=COLUMN_NAMES, font=('思源黑体 CN', 15, 'bold'), width=15)
    default_sort_column = COLUMN_NAMES[0]
    combo_sort_column.set(default_sort_column)
    combo_sort_column.place(x=140, y=618)

    # 排序按钮
    sort_button = tk.Button(root, text="单击排序", command=sort_button_click, font=('思源黑体 CN', 15, 'bold'))
    sort_button.place(x=55, y=660)

    # 启动主循环
    root.mainloop()


link_start_ultra()