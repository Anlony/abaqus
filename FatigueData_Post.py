import xlsxwriter
import numpy as np
import pandas as pd
import re
import math
import datetime
import numpy as np
import pandas as pd
import sys
import os
from openpyxl import load_workbook


# 程序初始化
start_time = datetime.datetime.now()
print('程序开始时间：%s' % (start_time))

##钢材弹模
E_s = 206e3

##读取热点应力数据

File_Name = ['10.21', '12.44', '14.41', '16.45', '18.40', '20.30', '21.10']
for name in range(1, 12):
    Date = '0605'
    Time = '%s' %name
    Data_path = 'E:/%s/数据处理/%s/%s.txt' %(Date, Time, Time)
    Df_Data = pd.read_csv(Data_path, index_col=[0], header=[0], sep='\t')
    Df_Data.columns = Df_Data.columns.str.replace(' ', '') ##原始数据中列标题存在大量空格
    Df_Data = Df_Data.drop(Df_Data.index[0]) ##原始数据第一行为空白
    Df_Data = Df_Data.reset_index(drop=True)

    ##创建输处excel文件
    Save_path = 'E:/%s/数据处理/%s/AG-Stress.xlsx'%(Date, Time)
    df = pd.DataFrame()
    writer = pd.ExcelWriter(Save_path, mode='w')
    writer.close()

    ##应变数据提取
    Df_AG_d = Df_Data[['绝对时间', '相对时间']]
    Mark_Gauge = ['01_04_03', '01_04_04', '01_02_01', '01_03_03', '01_03_04', '01_03_01']
    for i in Mark_Gauge:
        Pick_Data = Df_Data['%s' %i]
        Df_AG_d = pd.concat([Df_AG_d, Pick_Data], axis = 1)
    Df_AG_d.columns = [['时间', '时间', 'd', 'd', 'd', 'e', 'e', 'e'], 
        ['绝对时间', '相对时间', 'S1', 'S2', 'S3', 'S1', 'S2', 'S3']]


    ##获取应力数据
    Df_AG_d_Stress = Df_AG_d.copy()
    for i in range(2, Df_AG_d_Stress.shape[1]):
        Df_AG_d_Stress.iloc[:, i] = Df_AG_d_Stress.iloc[:, i] * E_s/1000000

    ##定位第一个循环的谷点和峰值点
    Low_idx = Df_AG_d_Stress.iloc[15:45, 2].idxmin()
    High_idx = Df_AG_d_Stress.iloc[15:45, 2].idxmax()
    ##循环次数
    Low_Cycles = (Df_AG_d_Stress.shape[0] - Low_idx) // 25
    High_Cycles = (Df_AG_d_Stress.shape[0] - Low_idx) // 25

    ##取出每个循环的谷值和峰值
    '''Low_Stress = pd.DataFrame()
    for  i in range(0, 2 * Low_Cycles):
        Data_index = Low_idx 
        if i == Df_AG_d_Stress.iloc[Data_index-5:Data_index+5 , 9].idxmin():
            Data_index = i
        else:
            Data_index = Df_AG_d_Stress.iloc[Data_index-5:Data_index+5 , 9].idxmin()
        Stress_Data = Df_AG_d_Stress.iloc[Data_index , :]
        Stress_Data = Stress_Data.to_frame().T
        Low_Stress = pd.concat([Low_Stress, Stress_Data], axis=0)
        if Data_index + 25 < Df_AG_d_Stress.shape[0]:
            Low_idx = Data_index + 25
        else:
             break'''##因为数据中含有异常零点，需根据峰值去取对应的谷值

    High_Stress = pd.DataFrame()
    for  i in range(0, 2*High_Cycles):
        Data_index = High_idx
        if Data_index == Df_AG_d_Stress.iloc[Data_index-5:Data_index+5 , 2].idxmax():
            pass
        else:
            Data_index = Df_AG_d_Stress.iloc[Data_index-5:Data_index+5 , 2].idxmax()
        Stress_Data = Df_AG_d_Stress.iloc[Data_index , :]
        Stress_Data = Stress_Data.to_frame().T
        High_Stress = pd.concat([High_Stress, Stress_Data], axis=0)
        if Data_index + 25 < Df_AG_d_Stress.shape[0]:
            High_idx = Data_index + 25
        else:
             break
    ##去掉第一个循环和最后一个循环
    High_Stress = High_Stress.drop(High_Stress.index[[0, -1]])
    ##根据峰值去取对应的谷值
    Low_Stress = pd.DataFrame()
    Low_idx = High_Stress.index.to_list()
    for  i in Low_idx: 
        Data_index = i - 12
        if Data_index == Df_AG_d_Stress.iloc[Data_index-1:Data_index+1, 2].idxmin():
            pass
        else:
            Data_index = Df_AG_d_Stress.iloc[Data_index-1:Data_index+1, 2].idxmin()
        Stress_Data = Df_AG_d_Stress.iloc[Data_index, :]
        Stress_Data = Stress_Data.to_frame().T
        Low_Stress = pd.concat([Low_Stress, Stress_Data], axis=0)
    with pd.ExcelWriter(Save_path, engine='openpyxl', mode='a') as writer:
            Df_AG_d.to_excel(writer, sheet_name='应变')
            Df_AG_d_Stress.to_excel(writer, sheet_name='应力')



    Low_Stress  = Low_Stress.reset_index()
    High_Stress = High_Stress.reset_index()

    ##除去检测过程中，应变片故障零点
    Zero_Index = []
    for i in range(0, Low_Stress.shape[0]):
        if Low_Stress.iloc[i, 3] == 0:
            Zero_Index.append(i)
        else:
             pass
    Low_Stress = Low_Stress.drop(Zero_Index)
    High_Stress = High_Stress.drop(Zero_Index)


    ##每个循环的均值
    Mean_Stress = (Low_Stress.iloc[:, 3:] + High_Stress.iloc[:, 3:])/2
    Mean_Stress = Mean_Stress.reset_index(drop=True)

    ##每个循环的幅值
    Ampli_Stress = High_Stress.iloc[:, 3:] - Low_Stress.iloc[:, 3:]
    Ampli_Stress = Ampli_Stress.reset_index(drop=True)


    ##写入文件
    with pd.ExcelWriter(Save_path, engine='openpyxl', mode='a') as writer:
            Low_Stress.to_excel(writer, sheet_name='谷值')
            High_Stress.to_excel(writer, sheet_name='峰值')
            Mean_Stress.to_excel(writer, sheet_name='均值')
            Ampli_Stress.to_excel(writer, sheet_name='幅值')

# 程序结束
end_time = datetime.datetime.now()
print('程序结束时间：%s' % (end_time))
print('程序所用时间：%s' % (end_time - start_time))




