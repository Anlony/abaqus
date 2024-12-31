import pandas as pd
import numpy as np
import os
from scipy.optimize import curve_fit 

def find_nearest_positions(column, targets):
    positions = []
    for target in targets:
        absolute_diff = (column - target).abs()
        nearest_index = absolute_diff.idxmin()
        positions.append(nearest_index)
    return sorted(positions)
def linear_interpolation(x1, y1, x2, y2, x3):
    # 计算斜率
    m = (y2 - y1) / (x2 - x1)
    # 计算截距
    b = y1 - m * x1
    # 计算y3
    y3 = m * x3 + b
    return y3
def quadratic_extrapolation(x1, y1, x2, y2, x3, y3, x4):
    # 建立方程组
    A = np.array([
        [x1**2, x1, 1],
        [x2**2, x2, 1],
        [x3**2, x3, 1]
    ])
    B = np.array([y1, y2, y3])
    
    # 解方程组，得到a, b, c
    a, b, c = np.linalg.solve(A, B)
    
    # 计算y4
    y4 = a * x4**2 + b * x4 + c
    return y4
def inverse_proportionality(x, a, b):
    return a*x+b

name_list = ['1-2', '1-3', '1-5', '2-2', '2-3', '2-4', '3-3', '3-4', '3-5', '4-2', '4-4', '4-5', '5-2', '5-4', '5-5']
groupName = 'GF'
##创建输出excel文件
filePath = 'E:/钢管混凝土/斜杆节点/整体模型-不带焊缝/HIC/%s/' %groupName
fileName = filePath + '%s.xlsx' %groupName
if not os.path.exists(filePath):
    os.makedirs(filePath)
writer = pd.ExcelWriter(fileName, mode='w')
writer.close()
dataFile = filePath + 'CON-'
for MODEL_i in name_list:
    pickedData = pd.read_csv(dataFile +'%s-%s.CSV'%(groupName, MODEL_i), usecols=['CutZ', 'FrameId', 'Fy']) 
    sorted_Data = pickedData.sort_values(by='FrameId')
    shearForce = pd.DataFrame()
    Z_cor = sorted_Data.iloc[0:50,:].sort_values(by='CutZ')['CutZ'].reset_index(drop=True)
    shearForce = pd.concat([shearForce, Z_cor], axis = 1)
    for i in range(0, int(sorted_Data.shape[0]/50)):
        data = sorted_Data.iloc[50*i:50*(i+1), :].sort_values(by='CutZ')['Fy']
        data = data.reset_index(drop=True)
        shearForce = pd.concat([shearForce, data], axis = 1)
    
    Z_list = list(Z_cor)
    ini_data = shearForce.iloc[:, 3].copy()
    d = 175
    mid_point = max(Z_list)/2
    outPut = pd.DataFrame()
    outPut = pd.concat([outPut, Z_cor], axis = 1)
    for col_i in range(3, shearForce.shape[1]): 
        new_col = shearForce.iloc[:, col_i] - ini_data 
        Fy_data = list(new_col)
        x_data = [z for z in Z_list if (mid_point-d) < z < (mid_point+d)]
        y_data = [a for z, a in zip(Z_list, Fy_data) if (mid_point-d) < z < (mid_point+d)]
        popt, pcov = curve_fit(inverse_proportionality, x_data, y_data) 
        HIC = popt[0] 
        # 在每一列的最后一行添加 HIC 值，并设置索引为 'HIC'
        new_col.loc['HIC'] = HIC
        # 使用 concat 将新列添加到 outPut DataFrame
        outPut = pd.concat([outPut, new_col.rename(shearForce.columns[col_i])], axis=1) 
    with pd.ExcelWriter(fileName, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        outPut.to_excel(writer, sheet_name='%s-%s' %(groupName, MODEL_i)) 

