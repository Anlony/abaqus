import  datetime
import numpy as np
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
import os
import math
from matplotlib.ticker import MultipleLocator

# 程序初始化
start_time = datetime.datetime.now()
print('程序开始时间：%s' % (start_time))

##矩阵滤波
def denoise_SVD(t, x):
    res = int(np.sqrt(len(x)))
    xr = x[:res * res]
    delay = t[:res * res]

    x2list = []
    for i in range(res):
        x2list.append(xr[i * res: i * res + res])
    x2array = np.array(x2list)

    U, S, V = np.linalg.svd(x2array)
    S_list = list(S)
    S_sum = sum(S)
    S_normalization_list = [x / S_sum for x in S_list]

    # 选择保留的奇异值阶数 K
    K = 1
    for i in range(len(S_list) - K):
        S_list[i + K] = 0.0
    S_new = np.mat(np.diag(S_list))
    reduceNoiseMat = np.array(U * S_new * V)
    reduceNoiseList = []
    for i in range(len(x2array)):
        for j in range(len(x2array)):
            reduceNoiseList.append(reduceNoiseMat[i][j])

    return (delay, reduceNoiseList)

##均值滤波
def ava_filter(x, filt_length):
    N = len(x)
    res = []
    for i in range(N):
        if i <= filt_length // 2 or i >= N - (filt_length // 2):
            temp = x[i]
        else:
            sum = 0
            for j in range(filt_length):
                sum += x[i - filt_length // 2 + j]
            temp = sum * 1.0 / filt_length
        res.append(temp)
    return res

def denoise_Ave(t, x, n, filt_length):
    for i in range(n):
        res = ava_filter(x, filt_length)
        x = res
    return (t, res)


File_Name = ['2']
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文

for name in File_Name:
    Date = '0607'
    Time = '%s' %name
    Data_path = 'E:/试验记录/GA-1/%s/数据处理/%s/AG-Stress.xlsx'%(Date, Time)
    Data_Mean = pd.read_excel(Data_path, index_col=[0], header=[0,1], nrows=12500, sheet_name='均值')
    Data_Ampl = pd.read_excel(Data_path, index_col=[0], header=[0,1], nrows=12500, sheet_name='幅值')
    #Data_Mean = Data_Mean.iloc[1000:, :]
    #Data_Ampl = Data_Ampl.iloc[1000:, :]

    #plt.figure(figsize=(8, 6))
    #plt.axis()

    plt.rc('font', size=14)  # 控制默认文本大小
    plt.rc('axes', titlesize=14)  # 坐标轴标题的字体大小
    plt.rc('axes', labelsize=14)  # x 和 y 轴标签的字体大小
    plt.rc('xtick', labelsize=14)  # x 轴刻度标签的字体大小
    plt.rc('ytick', labelsize=14)  # y 轴刻度标签的字体大小
    plt.rc('legend', fontsize=14)  # 图例的字体大小
    plt.rc('figure', titlesize=18)  # 图形标题的字体大小

    # 设置全局次刻度线间隔为主刻度线的1/10
    plt.rcParams["ytick.minor.visible"] = True
    plt.rcParams["ytick.minor.size"] = 1.8
    plt.rcParams["ytick.minor.width"] = 1
    plt.rcParams["ytick.minor.pad"] = 3
    plt.rcParams["ytick.minor.right"] = True
    
    # 设置 x 轴和 y 轴的刻度线朝内
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 设置 y 轴的次刻度线
    plt.minorticks_on()

    fig1,ds_mean = plt.subplots()
    fig2,es_mean = plt.subplots()
    fig3,ds_ampl = plt.subplots()
    fig4,es_ampl = plt.subplots()

    x = Data_Mean.index
     
    x1, y1 = denoise_Ave(x, list(Data_Mean['d']['S1']), 5, 50)
    x2, y2 = denoise_Ave(x, list(Data_Mean['d']['S2']), 5, 50)
    x3, y3 = denoise_Ave(x, list(Data_Mean['d']['S3']), 5, 50)
    ds_mean.plot(x1, y1, label="D-S1")
    ds_mean.plot(x2, y2, label="D-S2")
    ds_mean.plot(x3, y3, label="D-S3")
    ds_mean.set_xlabel("周期")
    ds_mean.set_ylabel("应力均值")
    ds_mean.legend()
    ds_mean.set_title("D-应力均值")
    #ds_mean.set_ylim(120, 150)
    #ds_mean.set_xlim(0, 2000)

    x4, y4 = denoise_Ave(x, list(Data_Mean['e']['S1']), 5, 50)
    x5, y5 = denoise_Ave(x, list(Data_Mean['e']['S2']), 5, 50)
    x6, y6 = denoise_Ave(x, list(Data_Mean['e']['S3']), 5, 50)
    es_mean.plot(x4, y4, label="E-S1")
    es_mean.plot(x5, y5, label="E-S2")
    es_mean.plot(x6, y6, label="E-S3")
    es_mean.set_xlabel("周期")
    es_mean.set_ylabel("应力均值")
    es_mean.legend()
    es_mean.set_title("E-应力均值")
    ##es_mean.set_ylim(120, 145)

    x7, y7 = denoise_Ave(x, list(Data_Ampl['d']['S1']), 5, 50)
    x8, y8 = denoise_Ave(x, list(Data_Ampl['d']['S2']), 5, 50)
    x9, y9 = denoise_Ave(x, list(Data_Ampl['d']['S3']), 5, 50)
    ds_ampl.plot(x7, y7, label="D-S1")
    ds_ampl.plot(x8, y8, label="D-S2")
    ds_ampl.plot(x9, y9, label="D-S3")
    ds_ampl.set_xlabel("周期")
    ds_ampl.set_ylabel("应力幅值")
    ds_ampl.legend()
    ds_ampl.set_title("D-应力幅值")
    #ds_ampl.set_ylim(138, 144)  # 设置 y 轴的上下限
    #ds_ampl.set_xlim(0, 2000)
    

    x10, y10 = denoise_Ave(x, list(Data_Ampl['e']['S1']), 5, 50)
    x11, y11 = denoise_Ave(x, list(Data_Ampl['e']['S2']), 5, 50)
    x12, y12 = denoise_Ave(x, list(Data_Ampl['e']['S3']), 5, 50)
    es_ampl.plot(x10, y10, label="E-S1")
    es_ampl.plot(x11, y11, label="E-S2")
    es_ampl.plot(x12, y12, label="E-S3")
    es_ampl.set_xlabel("周期")
    es_ampl.set_ylabel("应力幅值")
    es_ampl.legend()
    es_ampl.set_title("E-应力幅值")
    #es_ampl.set_ylim(130, 150)  # 设置 y 轴的上下限
    
    print("均值", "d-s1:%s" %np.mean(y1), "d-s2:%s"%np.mean(y2), "d-s3:%s"%np.mean(y3))
    print("幅值", "d-s1:%s" %np.mean(y7), "d-s2:%s"%np.mean(y8), "d-s3:%s"%np.mean(y9))
    print("均值", "e-s1:%s" %np.mean(y4), "e-s2:%s"%np.mean(y5), "e-s3:%s"%np.mean(y6))
    print("幅值", "e-s1:%s" %np.mean(y10), "e-s2:%s"%np.mean(y11), "e-s3:%s"%np.mean(y12))

    
    fig1.savefig('E:/GA-1/%s/数据处理/%s/Denoise-AG-D-均值.png'%(Date, Time), bbox_inches='tight', pad_inches=0.1, dpi=200)
    fig2.savefig('E:/GA-1/%s/数据处理/%s/Denoise-AG-E-均值.png'%(Date, Time), bbox_inches='tight', pad_inches=0.1, dpi=200)
    fig3.savefig('E:/GA-1/%s/数据处理/%s/Denoise-AG-D-幅值.png'%(Date, Time), bbox_inches='tight', pad_inches=0.1, dpi=200)
    fig4.savefig('E:/GA-1/%s/数据处理/%s/Denoise-AG-E-幅值.png'%(Date, Time), bbox_inches='tight', pad_inches=0.1, dpi=200)





# 程序结束
end_time = datetime.datetime.now()
print('程序结束时间：%s' % (end_time))
print('程序所用时间：%s' % (end_time - start_time))
