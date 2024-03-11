n = 32
r = 2000

Y_coordinate = [111.87E+03]
for i in Y_coordinate:
    for j in range(1, 33):
        matserinstance_name = 'singlepresteel-%r' %j
        slaveinstance_namne = 'maoban-t-1'
        contact_name = 'pre-t-%r' %j 
        initialpoint = (r, i, 0)
        positionpoint = (initialpoint[0]*math.cos(2*math.pi/n*(j-1)), initialpoint[1], -initialpoint[0]*math.sin(2*math.pi/n*(j-1)))
        toppoint = (positionpoint[0], positionpoint[1]+10, positionpoint[2])
        bottompoint = (positionpoint[0], positionpoint[1]-10, positionpoint[2])
        #point1 = (positionpoint[0]+(D_bolt+5)/2*math.cos(math.pi/4), positionpoint[1]+(D_bolt+5)/2*math.cos(math.pi/4), positionpoint[2])
        v = a.instances['%s' %matserinstance_name].vertices
        verts = v.getByBoundingCylinder(toppoint , bottompoint, 210)
        region1=regionToolset.Region(vertices=verts)
        s = a.instances['%s' %slaveinstance_namne].faces
        side1Faces = s.getByBoundingCylinder(toppoint , bottompoint, 210)
        region2=regionToolset.Region(side1Faces=side1Faces)
        m.Coupling(name='%s' %contact_name, 
            controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
            localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
