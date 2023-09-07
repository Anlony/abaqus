import xlrd
import math

from abaqus import *
from abaqusConstants import *
import __main__

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

##modelName
mdb.Model(name='tower', modelType=STANDARD_EXPLICIT)
a = mdb.models['tower'].rootAssembly

##towerBody
#getoordinate
file_inipath = 'E:/temp/concret_tower/input.xlsx'

workbook = xlrd.open_workbook(file_inipath)
coordinata_sheet = workbook.sheet_by_name('coordinate')
bottomsection_sheet = workbook.sheet_by_name('bottom_section')
topsection_sheet = workbook.sheet_by_name('top_section')

pointlist = [coordinata_sheet.row_values(row) for row in range(coordinata_sheet.nrows)]
bottomsectionlist = [bottomsection_sheet.row_values(row) for row in range(bottomsection_sheet.nrows)]
topsectionlist = [topsection_sheet.row_values(row) for row in range(topsection_sheet.nrows)]

mdb.Model(name='tower', modelType=STANDARD_EXPLICIT)
a = mdb.models['tower'].rootAssembly

whole_pieces = [22, 35]

##creat property
file_inipath1 = 'E:/temp/concret_tower/concrete_constitutive.xlsx'
workbook1 = xlrd.open_workbook(file_inipath1)
compression_sheet = workbook1.sheet_by_name('compression')
tension_sheet = workbook1.sheet_by_name('tension')
compression_strain = [(compression_sheet.cell_value(row, 0), compression_sheet.cell_value(row, 1)) for row in range(compression_sheet.nrows)]
compression_damage = [(compression_sheet.cell_value(row, 2), compression_sheet.cell_value(row, 3)) for row in range(compression_sheet.nrows)]
tension_strain = [(tension_sheet.cell_value(row, 0), tension_sheet.cell_value(row, 1)) for row in range(tension_sheet.nrows)]
tension_damage = [(tension_sheet.cell_value(row, 2), tension_sheet.cell_value(row, 3)) for row in range(tension_sheet.nrows)]

mdb.models['tower'].Material(name='con')
mdb.models['tower'].materials['con'].Density(table=((2400.0e-12, ), ))
mdb.models['tower'].materials['con'].Elastic(table=((37968.7, 0.2), ))
mdb.models['tower'].materials['con'].ConcreteDamagedPlasticity(table=((30.0, 
    0.1, 1.16, 0.6667, 0.0005), ))
mdb.models['tower'].materials['con'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=compression_strain)
mdb.models['tower'].materials['con'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=tension_strain)
mdb.models['tower'].materials['con'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=compression_damage)
mdb.models['tower'].materials['con'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=tension_damage)
mdb.models['tower'].HomogeneousSolidSection(name='con', material='con', 
    thickness=None)

##towerBody_line
#getoordinate
for i in range(0, len(bottomsectionlist)):
    s = mdb.models['tower'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    ##1,4-outside, 2,4-inside
      
    vertex_1 = (bottomsectionlist[i][0],pointlist[i][1])
    vertex_2 = (bottomsectionlist[i][0]-bottomsectionlist[i][1], pointlist[i][1])
    vertex_3 = (topsectionlist[i][0]-topsectionlist[i][1], pointlist[i+1][1])
    vertex_4 = (topsectionlist[i][0],pointlist[i+1][1])
    if i == 35:##the lastest concreattower section
        vertex_4 = (1670, pointlist[i+1][1])
        vertex_3 = (1890, pointlist[i][1]+830)
        vertex_5 = (topsectionlist[i][0],pointlist[i+1][1])
    else:
        pass
    s.setPrimaryObject(option=STANDALONE)
    s.ConstructionLine(point1=(0.0, -5000.0), point2=(0.0, 5000.0))
    s.Line(point1=vertex_1, point2=vertex_2)
    s.Line(point1=vertex_2, point2=vertex_3)
    s.Line(point1=vertex_3, point2=vertex_4)
    if i == 35:##the lastest concreattower section
        s.Line(point1=vertex_4, point2=vertex_5)
        s.Line(point1=vertex_5, point2=vertex_1)
    else:
        s.Line(point1=vertex_4, point2=vertex_1)
        
    p = mdb.models['tower'].Part(name='p-%r' %(i+1), dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['tower'].parts['p-%r' %(i+1)]
    if i in whole_pieces:
        p.BaseSolidRevolve(sketch=s, angle=360.0, flipRevolveDirection=OFF)
    else:
        p.BaseSolidRevolve(sketch=s, angle=90.0, flipRevolveDirection=OFF)
    s.unsetPrimaryObject()
    p = mdb.models['tower'].parts['p-%r' %(i+1)]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['tower'].sketches['__profile__']

    ## property_assign
    p = mdb.models['tower'].parts['p-%r' %(i+1)]
    c = p.cells
    region = regionToolset.Region(cells=c)
    p = mdb.models['tower'].parts['p-%r' %(i+1)]
    p.SectionAssignment(region=region, sectionName='con', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)## property_assign

    a = mdb.models['tower'].rootAssembly
    p = mdb.models['tower'].parts['p-%r' %(i+1)]
    a.Instance(name='p-%r' %(i+1), part=p, dependent=ON)

    ##creat surface_set
    a = mdb.models['tower'].rootAssembly
    
    if i in whole_pieces:
        pass
        '''a.RadialInstancePattern(instanceList=('p-%r' %(i+1), ), point=(0.0, 0.0, 0.0), 
        axis=(0.0, 1.0, 0.0), number=2, totalAngle=360.0)
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r' %(i+1), 
        toName='p-%r-1' %(i+1))
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r' %(i+1), 
            toName='p-%r-2' %(i+1))
        
        midpoint1 = ( (vertex_1[0]+vertex_5[0])/2, (vertex_1[1]+vertex_5[1])/2, 0) 
        midpoint2 = (-(vertex_1[0]+vertex_5[0])/2, (vertex_1[1]+vertex_5[1])/2, 0) 

        s = a.instances['p-%r-1' %(i+1)].faces
        side1Faces1 = s.findAt((midpoint1,))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs1' %(i+1))
        
        s = a.instances['p-%r-2' %(i+1)].faces
        side1Faces1 = s.findAt((midpoint1,))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs2' %(i+1))

        s = a.instances['p-%r-1' %(i+1)].faces
        side1Faces1 = s.findAt((midpoint2,))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs3' %(i+1))
        
        s = a.instances['p-%r-2' %(i+1)].faces
        side1Faces1 = s.findAt((midpoint2,))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs4' %(i+1))


        midpoint3 = ( (vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2, 5) 
        midpoint4 = ( (vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2, -5) 
        s1 = a.instances['p-%r-1' %(i+1)].faces
        side1Faces1 = s1.findAt((midpoint3,))
        s2 = a.instances['p-%r-2' %(i+1)].faces
        side1Faces2 = s2.findAt((midpoint4,))
        a.Surface(side1Faces=side1Faces1+side1Faces2, name='p-%r-hb' %(i+1))

        midpoint5 = ( (vertex_4[0]+vertex_5[0])/2, (vertex_4[1]+vertex_5[1])/2, 5) 
        midpoint6 = ( (vertex_4[0]+vertex_5[0])/2, (vertex_4[1]+vertex_5[1])/2, -5) 
        s1 = a.instances['p-%r-1' %(i+1)].faces
        side1Faces1 = s1.findAt((midpoint5,))
        s2 = a.instances['p-%r-2' %(i+1)].faces
        side1Faces2 = s2.findAt((midpoint6,))
        a.Surface(side1Faces=side1Faces1+side1Faces2, name='p-%r-ht' %(i+1))

        a.rotate(instanceList=('p-%r-1' %(i+1), 'p-%r-2' %(i+1)), axisPoint=(0.0, 
        0, 0.0), axisDirection=(0.0, -10.0, 0.0), angle= i*45%360)'''

    else:
        a.RadialInstancePattern(instanceList=('p-%r' %(i+1), ), point=(0.0, 0.0, 0.0), 
        axis=(0.0, 1.0, 0.0), number=4, totalAngle=360.0)
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r' %(i+1), 
        toName='p-%r-1' %(i+1))
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r-rad-2' %(i+1), 
            toName='p-%r-2' %(i+1))
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r-rad-3' %(i+1), 
        toName='p-%r-3' %(i+1))
        mdb.models['tower'].rootAssembly.features.changeKey(fromName='p-%r-rad-4' %(i+1), 
        toName='p-%r-4' %(i+1))

        partnamelist = ['p-%r-1' %(i+1), 'p-%r-2' %(i+1),'p-%r-3' %(i+1), 'p-%r-4' %(i+1)]
        midpointlist = [] 
        for midpoint_i in range(0,4):
            midpoint = ((vertex_2[0]+vertex_4[0])/2*math.cos(math.radians(90*midpoint_i)),
                (vertex_2[1]+vertex_4[1])/2,-(vertex_2[0]+vertex_4[0])/2*math.sin(math.radians(90*midpoint_i)))##anticlockwise
            midpointlist.append(midpoint)

        s = a.instances[partnamelist[0]].faces
        side1Faces1 = s.findAt((midpointlist[0],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs1' %(i+1))

        s = a.instances[partnamelist[1]].faces
        side1Faces1 = s.findAt((midpointlist[0],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs2' %(i+1))

        s = a.instances[partnamelist[1]].faces
        side1Faces1 = s.findAt((midpointlist[1],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs3' %(i+1))

        s = a.instances[partnamelist[2]].faces
        side1Faces1 = s.findAt((midpointlist[1],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs4' %(i+1))

        s = a.instances[partnamelist[2]].faces
        side1Faces1 = s.findAt((midpointlist[2],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs5' %(i+1))

        s = a.instances[partnamelist[3]].faces
        side1Faces1 = s.findAt((midpointlist[2],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs6' %(i+1))

        s = a.instances[partnamelist[3]].faces
        side1Faces1 = s.findAt((midpointlist[3],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs7' %(i+1))

        s = a.instances[partnamelist[0]].faces
        side1Faces1 = s.findAt((midpointlist[3],))
        a.Surface(side1Faces=side1Faces1, name='p-%r-vs8' %(i+1))
  
        midpoint1 = ( (vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2, 5)
        midpoint2 = ( (vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2,-5)
        midpoint3 = (-(vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2,-5)   
        midpoint4 = (-(vertex_1[0]+vertex_2[0])/2, (vertex_1[1]+vertex_2[1])/2, 5)  
        s1 = a.instances[partnamelist[0]].faces
        side1Faces1 = s1.findAt((midpoint1,))
        s2 = a.instances[partnamelist[1]].faces
        side1Faces2 = s2.findAt((midpoint2,))
        s3 = a.instances[partnamelist[2]].faces
        side1Faces3 = s3.findAt((midpoint3,))
        s4 = a.instances[partnamelist[3]].faces
        side1Faces4 = s4.findAt((midpoint4,))
        a.Surface(side1Faces=side1Faces1+side1Faces2+side1Faces3+side1Faces4, 
        name='p-%r-hb' %(i+1))

        midpoint1 = ( (vertex_3[0]+vertex_4[0])/2, (vertex_3[1]+vertex_4[1])/2, 5)
        midpoint2 = ( (vertex_3[0]+vertex_4[0])/2, (vertex_3[1]+vertex_4[1])/2,-5)
        midpoint3 = (-(vertex_3[0]+vertex_4[0])/2, (vertex_3[1]+vertex_4[1])/2,-5)   
        midpoint4 = (-(vertex_3[0]+vertex_4[0])/2, (vertex_3[1]+vertex_4[1])/2, 5)      
        s1 = a.instances[partnamelist[0]].faces
        side1Faces1 = s1.findAt((midpoint1,))
        s2 = a.instances[partnamelist[1]].faces
        side1Faces2 = s2.findAt((midpoint2,))
        s3 = a.instances[partnamelist[2]].faces
        side1Faces3 = s3.findAt((midpoint3,))
        s4 = a.instances[partnamelist[3]].faces
        side1Faces4 = s4.findAt((midpoint4,))
        a.Surface(side1Faces=side1Faces1+side1Faces2+side1Faces3+side1Faces4, 
        name='p-%r-ht' %(i+1))
 
        a.rotate(instanceList=('p-%r-1' %(i+1), 'p-%r-2' %(i+1), 'p-%r-3' %(i+1), 'p-%r-4' %(i+1)), axisPoint=(0.0, 
        0, 0.0), axisDirection=(0.0, -10.0, 0.0), angle= i*45%360)
