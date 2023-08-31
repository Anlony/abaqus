##modelName
Mdb(pathName='E:/temp/concret_tower/new_test.cae')
mdb.Model(name='tower', modelType=STANDARD_EXPLICIT)
a = mdb.models['tower'].rootAssembly

##towerBody_line
#getoordinate
file_inipath = 'E:/temp/concret_tower/input.xlsx'

workbook = xlrd.open_workbook(file_inipath)
coordinata_sheet = workbook.sheet_by_name('coordinate')
bottomsection_sheet = workbook.sheet_by_name('bottom_section')
topsection_sheet = workbook.sheet_by_name('top_section')

pointlist = [coordinata_sheet.row_values(row) for row in range(coordinata_sheet.nrows)]
bottomsectionlist = [bottomsection_sheet.row_values(row) for row in range(bottomsection_sheet.nrows)]
topsectionlist = [topsection_sheet.row_values(row) for row in range(topsection_sheet.nrows)]

s = mdb.models['tower'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints

for cor_i in range(0,len(pointlist)-1):
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=pointlist[cor_i], point2=pointlist[cor_i+1])
p = mdb.models['tower'].Part(name='towerbody', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['tower'].parts['towerbody']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['tower'].parts['towerbody']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['tower'].sketches['__profile__']

##property
#property_difinite
mdb.models['tower'].Material(name='s')
mdb.models['tower'].materials['s'].Density(table=((7850.0e-12, ), ))
mdb.models['tower'].materials['s'].Elastic(table=((200e3, 0.3), ))
mdb.models['tower'].Material(name='c80')
mdb.models['tower'].materials['c80'].Density(table=((2500.0e-12, ), ))
mdb.models['tower'].materials['c80'].Elastic(table=((38e3, 0.2), ))
mdb.models['tower'].Material(name='rigid')
mdb.models['tower'].materials['rigid'].Elastic(table=((1e10, 0.1), ))

#section_difinite
steel_start = 45  ##Notice!!!!
for section_i in range(0,len(bottomsectionlist)):
        mdb.models['tower'].PipeProfile(name='bottomsec-%r' %(section_i+1), r=bottomsectionlist[section_i][0], t=bottomsectionlist[section_i][1])
        mdb.models['tower'].PipeProfile(name='topsec-%r' %(section_i+1), r=topsectionlist[section_i][0], t=topsectionlist[section_i][1])
#section+property_difinite
for section_i in range(1,len(bottomsectionlist)+1):
    if section_i < steel_start:
        mdb.models['tower'].BeamSection(name='c-%r'%(section_i), integration=BEFORE_ANALYSIS, 
        poissonRatio=0.0, beamShape=TAPERED, profile='bottomsec-%r'%(section_i), profileEnd='topsec-%r' %(section_i), 
        density=2500.0e-12, thermalExpansion=OFF, temperatureDependency=OFF, dependencies=0, table=((38e3, 15.83e3), ), 
        alphaDamping=0.0, betaDamping=0.0, compositeDamping=0.0, centroid=(0.0, 0.0), shearCenter=(0.0, 0.0), consistentMassMatrix=True)     
    else:
        mdb.models['tower'].BeamSection(name='s-%r'%(section_i-steel_start+1), integration=BEFORE_ANALYSIS, 
        poissonRatio=0.0, beamShape=TAPERED, profile='bottomsec-%r'%(section_i), profileEnd='topsec-%r' %(section_i), 
        density=7850.0e-12, thermalExpansion=OFF, temperatureDependency=OFF, dependencies=0, table=((200e3, 76.92e3), ), 
        alphaDamping=0.0, betaDamping=0.0, compositeDamping=0.0, centroid=(0.0, 0.0), shearCenter=(0.0, 0.0), consistentMassMatrix=True)
mdb.models['tower'].BeamSection(name='rigid', integration=DURING_ANALYSIS, 
            poissonRatio=0.0, profile='topsec-%r' %(len(topsectionlist)-steel_start) , material='rigid', temperatureVar=LINEAR, consistentMassMatrix=False)

##property_assign
e = p.edges
for i in range(0,len(pointlist)-1):
    if i+1 < steel_start:
        midpoint = ((pointlist[i][0]+pointlist[i+1][0])/2,(pointlist[i][1]+pointlist[i+1][1])/2,0)
        edges = e.findAt((midpoint,))#the point must be localed on the edge
        region = regionToolset.Region(edges=edges)
        p.SectionAssignment(region=region, sectionName='c-%r' %(i+1), offset=0.0, 
            offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    else:
        if pointlist[i+1][0] == 0:
            midpoint = ((pointlist[i][0]+pointlist[i+1][0])/2,(pointlist[i][1]+pointlist[i+1][1])/2,0)
            edges = e.findAt((midpoint,))
            region = regionToolset.Region(edges=edges)
            p.SectionAssignment(region=region, sectionName='s-%r' %(i-steel_start+2), offset=0.0, 
                offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
        else:
            midpoint = ((pointlist[i][0]+pointlist[i+1][0])/2,(pointlist[i][1]+pointlist[i+1][1])/2,0)
            edges = e.findAt((midpoint,))
            region = regionToolset.Region(edges=edges)
            p.SectionAssignment(region=region, sectionName='rigid', offset=0.0, 
                offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

##beamorientation_assign
e = p.edges
for i in range(0,len(pointlist)-1):
    midpoint = ((pointlist[i][0]+pointlist[i+1][0])/2,(pointlist[i][1]+pointlist[i+1][1])/2,0)
    edges = e.findAt((midpoint,))#the point must be localed on the edges
    region = regionToolset.Region(edges=edges)
    p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

##casingpointproperty_difinite
v = p.vertices
verts = v.findAt(((pointlist[-2][0],pointlist[-2][1],0.0),))
region=regionToolset.Region(vertices=verts)
mdb.models['tower'].parts['towerbody'].engineeringFeatures.PointMassInertia(
    name='Inertia-1', region=region, mass=131, alpha=0.0, 
    composite=0.0)

verts = v.findAt(((pointlist[-1][0],pointlist[-1][1],0.0),))
region=regionToolset.Region(vertices=verts)
mdb.models['tower'].parts['towerbody'].engineeringFeatures.PointMassInertia(
    name='Inertia-2', region=region, mass=156, alpha=0.0, 
    composite=0.0)

p.AttachmentPoints(name='Masspoint', points=((0.0, 145774.0, 0.0), (0.0, 135774.0, 0.0)), 
    setName='Attachment Points-1-Set-2') #creat masspoint
v = p.vertices
verts =  v.findAt(((0.0, 145774.0, 0.0),))
region=regionToolset.Region(vertices=verts)
mdb.models['tower'].parts['towerbody'].engineeringFeatures.PointMassInertia(
    name='Inertia-3', region=region, mass=190.0, alpha=0.0, composite=0.0)

verts = v.findAt(((0.0, 135774.0, 0.0),))
region=regionToolset.Region(vertices=verts)
mdb.models['tower'].parts['towerbody'].engineeringFeatures.PointMassInertia(
    name='Inertia-4', region=region, mass=160, alpha=0.0, 
    composite=0.0)

##assembly
a.Instance(name='towerbody-1', part=p, dependent=ON)

##step
mdb.models['tower'].StaticStep(name='Step-1', previous='Initial', 
        initialInc=0.01)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
mdb.models['tower'].FrequencyStep(name='Step-2', previous='Step-1', 
    numEigen=20)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-2')

##load
v1 = a.instances['towerbody-1'].vertices
verts1 = v1.findAt(((pointlist[0][0],pointlist[0][1],0),))
region = regionToolset.Region(vertices=verts1)
mdb.models['tower'].DisplacementBC(name='BC-1', createStepName='Initial', 
    region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=SET, ur3=UNSET, 
    amplitude=UNSET, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

mdb.models['tower'].rootAssembly.engineeringFeatures.SpringDashpotToGround(
    name='Mx', region=region, orientation=None, dof=4, springBehavior=ON, 
    springStiffness=400e12, dashpotBehavior=OFF, 
    dashpotCoefficient=0.0)

mdb.models['tower'].rootAssembly.engineeringFeatures.SpringDashpotToGround(
    name='Mz', region=region, orientation=None, dof=6, springBehavior=ON, 
    springStiffness=400e12, dashpotBehavior=OFF, 
    dashpotCoefficient=0.0)

session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
mdb.models['tower'].Gravity(name='gravity', createStepName='Step-1', comp2=-9800, 
        distributionType=UNIFORM, field='')

##mesh
p.seedPart(size=10, deviationFactor=0.1, minSizeFactor=0.1)
elemType1 = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)
e = p.edges
for i in range(0,len(pointlist)-1):
    midpoint = ((pointlist[i][0]+pointlist[i+1][0])/2,(pointlist[i][1]+pointlist[i+1][1])/2,0)
    edges = e.findAt((midpoint,))#the point must be localed on the edges
    pickedRegions =(edges, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    p.generateMesh()

#regenerate feature
a = mdb.models['tower'].rootAssembly
a.regenerate()
session.viewports['Viewport: 1'].setValues(displayedObject=a)

##inp
a = mdb.models['tower'].rootAssembly
mdb.Job(name='j-0804', model='tower', description='', type=ANALYSIS, atTime=None, 
        waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=8, 
        numDomains=8, numGPUs=0)

