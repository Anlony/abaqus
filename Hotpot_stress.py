from abaqus import *
from abaqusConstants import *
import os

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior


modelName = 'FAT2'
filePath = 'E:/temp/FAT/%s-c' %modelName
if not os.path.exists(filePath):
    os.makedirs(filePath)
index_0 = 18290
n = session.odbs['E:/temp/FAT/%s-c.odb' %modelName].rootAssembly.instances['%s-1' %modelName].nodeSets['SET-1'].nodes
n_position = n[index_0-1].coordinates
n_coo = []
n1_coo =[]
index_list = []
for node_i in range(0, len(n)):
    n_coo_i = n[node_i].coordinates.tolist()
    n_coo.append(n_coo_i)
    if 200<n[node_i].coordinates[0]<=n_position[0] and 781<=n[node_i].coordinates[1]<=869 and n_position[2]<=n[node_i].coordinates[2]<=130:
        #n1_label = n[node_i].label
        n_coo_i.insert(0, node_i)
        n1_coo.append(n_coo_i)
sorted_y_list = sorted(n1_coo, key=lambda x: x[2], reverse=True)
sorted_z_list = sorted(n1_coo, key=lambda x: x[3])

segmented_y_lists = {}
key_y_list = []
for item in sorted_y_list:
    key = round(item[2],3)
    if key not in segmented_y_lists:
        segmented_y_lists[key] = []
        key_y_list.append(key)
    segmented_y_lists[key].append(item)

pathNode_tran_lists = {}
pathName_tran_list = []
for key_i in range(1, (len(key_y_list)+1)/2+1):
    nodeList = segmented_y_lists[key_y_list[2*(key_i-1)]]
    sorted_nodeList = sorted(nodeList, key=lambda x: x[3])
    for path_j in range(1, 6):
        #path_name ='Path-%s-%s' %(key_i+1, path_j)
        path_name ='Path-%s-%s' %(key_y_list[2*(key_i-1)], path_j)
        pathName_tran_list.append(path_name)
        pathNode_tran_lists[path_name] = []
        r1 = float(250.0-6.0/4.0*(path_j-1.0))
        node_label = []
        for node_i in range(0, len(sorted_nodeList)):
            x1_co = sorted_nodeList[node_i][1]
            y1_co = sorted_nodeList[node_i][2]
            z1_co = sorted_nodeList[node_i][3]
            r1_dis = (x1_co**2 + z1_co**2)**0.5
            if r1_dis < r1 + 0.2 and r1_dis > r1 - 0.2:
                node_label.append(n[sorted_nodeList[node_i][0]].label)
        pathNode_tran_lists[path_name].append(node_label[:11])
for pathName_i in range(0,len(pathName_tran_list)):
    new_pth = pathNode_tran_lists[pathName_tran_list[pathName_i]][0]
    session.Path(name=pathName_tran_list[pathName_i], type=NODE_LIST, expression=(('%s-1' %modelName, (new_pth)), ))

r1 = 250.0
filtered_z_list = [node_i for node_i in sorted_z_list if r1 - 0.3 <= (node_i[1]**2 + node_i[3]**2)**0.5 <= r1 + 0.3]


segmented_z_lists = {}
key_z_list = []
for item in filtered_z_list:
    key = round(item[3],3)
    if key not in segmented_z_lists:
        segmented_z_lists[key] = []
        key_z_list.append(key)
    segmented_z_lists[key].append(item)

pathNode_vert_lists = {}
pathName_vert_list = []
for key_i in range(2, 12):
    nodeList = segmented_z_lists[key_z_list[key_i-1]]
    sorted_nodeList = sorted(nodeList, key=lambda x: x[2])
    path_name ='Path-%s' %key_z_list[key_i-1]
    pathName_vert_list.append(path_name)
    pathNode_vert_lists[path_name] = []
    node_label = []
    for node_i in range(0, len(sorted_nodeList)):
        node_label.append(n[sorted_nodeList[node_i][0]].label)
    pathNode_vert_lists[path_name].append(node_label)
for pathName_i in range(0,len(pathName_vert_list)):
    new_pth = pathNode_vert_lists[pathName_vert_list[pathName_i]][0]
    session.Path(name=pathName_vert_list[pathName_i], type=NODE_LIST, expression=(('%s-1' %modelName, (new_pth)), ))
#segmented_y_lists = list(segmented_y_lists.values())



for i in range(1, (len(key_y_list)+1)/2+1):
    y_i = key_y_list[2*(i-1)]
    resultFileName = filePath + '/Path-%s' %i+ '.txt'
    content = ['%s' %y_i]
    for j in range(1, 6):
        new_content = []
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=0)
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
                COMPONENT, 'S22'))
        pth = session.paths['Path-%s-%s' %(y_i, j)]
        result_list = session.XYDataFromPath(name='XYData-%s-%s-%s' %(y_i, j, 0) , path=pth, includeIntersections=False, 
            projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, 
            projectionTolerance=0, shape=UNDEFORMED, labelType=Z_COORDINATE, 
            removeDuplicateXYPairs=True, includeAllElements=False)
        for line_i in range(0, len(result_list)):
            new_content.append(str(result_list[line_i][0]))
        for frame_i in range(0, 17):
            S_22 = []
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=frame_i)
            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
                COMPONENT, 'S22'))
            pth = session.paths['Path-%s-%s' %(y_i, j)]
            result_list = session.XYDataFromPath(name='XYData-%s-%s-%s' %(y_i, j, frame_i) , path=pth, includeIntersections=False, 
                projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, 
                projectionTolerance=0, shape=UNDEFORMED, labelType=Z_COORDINATE, 
                removeDuplicateXYPairs=True, includeAllElements=False)
            for line_i in range(0, len(result_list)):
                new_content[line_i] = new_content[line_i] + ',' + '%s' %(result_list[line_i][1])
        content = content + [''] + new_content
    #os.makedirs(os.path.dirname(resultFileName), exist_ok=True)
    with open(resultFileName, 'w') as f:
        f.truncate(0)
        for item in content:
            f.write(item + '\n')


for i in range(1, 11):
    z_i = key_z_list[i]
    resultFileName = filePath + '/Path-Y%s' %i+ '.txt'
    content = []
    content = ['%s' %z_i]
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=0)
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
            variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
            COMPONENT, 'S22'))
    pth = session.paths['Path-%s' %z_i]
    result_list = session.XYDataFromPath(name='XYData-%s-%s' %(z_i, 0) , path=pth, includeIntersections=True, 
        projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, 
        projectionTolerance=0, shape=UNDEFORMED, labelType=Y_COORDINATE, 
        removeDuplicateXYPairs=True, includeAllElements=False)
    for line_i in range(0, len(result_list)):
        content.append(str(result_list[line_i][0]))
    for frame_i in range(0, 17):
        S_22 = []
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=frame_i)
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
            variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
            COMPONENT, 'S22'))
        pth = session.paths['Path-%s' %z_i]
        result_list = session.XYDataFromPath(name='XYData-%s-%s' %(z_i, frame_i) , path=pth, includeIntersections=True, 
            projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, 
            projectionTolerance=0, shape=UNDEFORMED, labelType=Y_COORDINATE, 
            removeDuplicateXYPairs=True, includeAllElements=False)
        for line_i in range(0, len(result_list)):
            content[line_i] = content[line_i] + ',' + '%s' %(result_list[line_i][1])
    #os.makedirs(os.path.dirname(resultFileName), exist_ok=True)
    with open(resultFileName, 'w') as f:
        f.truncate(0)
        for item in content:
            f.write(item + '\n')
                
