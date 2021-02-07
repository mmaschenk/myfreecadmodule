import FreeCAD, FreeCADGui
import os
import Part
from math import sqrt
import numpy as np
import BOPTools.JoinFeatures
from BOPTools import JoinAPI

path = os.path.dirname(__file__)

uifile = os.path.join(path,"PlatonicSolid.ui")

platonicobjects = ["Cube", "Tetrahedron", "Octahedron", "Icosahedron", "Dodecahedron"]
radii = ["Outer radius", "Edge length"]

PHI = (1 + sqrt(5))/2
INVPHI = 1/PHI
KSI = sqrt((5-sqrt(5))/2)

platonic_solids = {
    'Tetrahedron': {
        'vertices' : [ (1,1,1), (1, -1, -1,), (-1, 1, -1), (-1, -1, 1) ],
        'faces': [ (0,1,2), (0,1,3), (0,3,2), (1,2,3)],
        'edges': [ (0,1), (0,2), (0,3), (1,2), (1,3), (2,3) ],
        'radius': sqrt(3),
        'edgelength': 2*sqrt(2), 
    },
    'Cube': {
        'vertices': [ (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                      (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)],
        'faces': [ (0,1,2,3), (1,2,6,5), (0,1,5,4), (0,3,7,4), (3,2,6,7), (4,5,6,7)],
        'edges': [ (0,1), (0,3), (0,3), (0,4), (1,2), (1,5), (2,3), (2,6),
                   (3,7), (4,5), (4,7), (5,6), (6,7)],
        'radius': sqrt(3),
        'edgelength': 2,
    },
    'Octahedron': {
        'vertices': [ (0, 0, -1), (-1,0,0), (0,-1,0), (1,0,0), (0,1,0), (0,0,1)],
        'faces': [ (0,1,2), (0,2,3), (0,3,4), (0,4,1), (5,1,2), (5,2,3), (5,3,4), (5,4,1)],
        'radius': 1,
        'edgelength': sqrt(2),
    },
    'Icosahedron': {
        'vertices': [ (0, 1, -PHI), (0, -1, -PHI), (-PHI, 0, -1), (PHI,0, -1), 
                      (-1,-PHI,0), (1, -PHI,0), (1, PHI, 0), (-1,PHI,0),
                      (-PHI,0, 1), (PHI,0,1), (0,1,PHI), (0,-1,PHI), ],

        'faces': [ (0,1,2), (0,1,3), (1,2,4), (1,4,5), (1,5,3), (3,5,9), (3,9,6),
                   (3,6,0), (0,6,7), (0,7,2), (2,7,8), (2,8,4), (4,8,11), (4,11,5),
                   (5,11,9), (9,10,6), (6,10,7), (7,10,8), (8,10,11), (11,10,9), ],
        'radius': KSI * PHI,
        'edgelength': 2,
    },
    'Dodecahedron': {
        'vertices': [ (-INVPHI, 0, -PHI), (INVPHI, 0, -PHI), 
                      (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), 
                      (0, -PHI, -INVPHI), (0, PHI, -INVPHI),
                      (-PHI,-INVPHI,0), (PHI, -INVPHI,0), (PHI,INVPHI,0),(-PHI,INVPHI,0),
                      (0, -PHI, INVPHI), (0, PHI, INVPHI),
                      (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1), 
                      (-INVPHI, 0, PHI), (INVPHI, 0, PHI), ],
        'faces': [ (0,1,3,6,2), (0,1,4,7,5), (0,2,8,11,5), (1,3,9,10,4),
                   (2,6,12,14,8), (3,9,15,12,6), (4, 7,13,16,10), (5,11,17,13,7),
                   (8,14,18, 17,11), (10,16,19,15,9), (13,17,18,19,16), (12,15,19,18,14)],
        'radius': sqrt(3),
        'edgelength': 2/PHI,
    }
}

def dirobject(obj, fmt):
    for i in dir(obj):
        print(fmt.format(i, getattr(obj,i)))

def normalize( tup, factor):
    return tuple( [x * factor for x in tup])

def vnormalize( tup, factor=1):
    return FreeCAD.Vector( tup[0]*factor, tup[1]*factor, tup[2]*factor)

def matricize(faces):
    def set(x,y):
        matrix[x][y] = True
        matrix[y][x] = True

    def unset(x,y):
        matrix[x][y] = False
        matrix[y][x] = False

    size = max([y for x in faces for y in x])+1
    matrix = np.zeros( (size,size), dtype=bool )

    for f in faces:
        lasti = None
        firsti = None
        for i in f:
            if lasti is not None:
                set(i,lasti)
            else:
                firsti = i
            lasti = i
        set(lasti,firsti)        
    return matrix

def cylindershapes(solid, factor=1, radius=0.2):
    p = platonic_solids[solid]
    faces = p['faces']
    verts = p['vertices']
    matrix = matricize(faces)

    shapes = []
    xrange,yrange = matrix.shape
    
    for x in range(xrange):
        for y in range(x+1,yrange):
            if matrix[x][y]:
                start = vnormalize(verts[x],factor)
                end = vnormalize(verts[y], factor)
                direction = end-start
                s = Part.makeCylinder(radius, direction.Length, start, direction)
                shapes.append(s)
    return shapes

def sphereshapes(solid, factor=1, radius=0.2):
    p = platonic_solids[solid]
    verts = p['vertices']

    shapes = []
    for v in verts:
        center = vnormalize(v, factor)
        s = Part.makeSphere(radius, center)
        shapes.append(s)
    return shapes

class PlatonicSolid:
    def __init__(self, obj):
        obj.addProperty("App::PropertyEnumeration", 
                        "Solid", 
                        "Platonic solid",
                        "Type of solid")
        obj.Solid = platonicobjects
        obj.Solid = 0
        obj.addProperty("App::PropertyEnumeration", 
                        "ActiveMeasure", 
                        "Platonic solid",
                        "Measure type active")
        obj.ActiveMeasure = radii
        obj.ActiveMeasure = 0
        obj.addProperty("App::PropertyBool", 
                        "VertexPolygon", 
                        "Platonic solid",
                        "Create vertices for polygon edges").VertexPolygon = False
        obj.addProperty("App::PropertyBool", 
                        "Cloud", 
                        "Platonic solid",
                        "Create cloud of spheres at vertices").VertexPolygon = False
        obj.addProperty("App::PropertyBool", 
                        "SolidObject", 
                        "Platonic solid",
                        "Create solid object").SolidObject = True
        obj.addProperty("App::PropertyLength", 
                        "OuterRadius", 
                        "Platonic solid",
                        "Outer Radius").OuterRadius = 10.0
        obj.addProperty("App::PropertyLength", 
                        "EdgeLength", 
                        "Platonic solid",
                        "Edge Length").EdgeLength = 5.0
        obj.addProperty("App::PropertyLength", 
                        "EdgeRadius", 
                        "Platonic solid",
                        "Edge Radius").EdgeRadius = 2.0


        self.Type = 'platonicSolid'
        obj.Proxy = self

    def execute(self, obj):
        FreeCAD.Console.PrintMessage("Recompute Python DecoratedCylinder feature\n")
        #c1 = Part.makeCylinder(obj.OuterRadius,20)
        #c2 = Part.makeCylinder(obj.OuterRadius*2,10)
        #rst = JoinAPI.connect([c1,c2], 0)
        #if selfobj.Refine:
        #    rst = rst.removeSplitter()
        #obj.Shape = rst


        #print("self = [{0}]. obj = [{1}]".format(self,obj))

        #dirobject(self, "Self[{0}] -> [{1}]")
        #dirobject(obj, "Obj[{0}] -> [{1}]")
        #rst = self.platonicsolid(obj)
        rst = self.cylinders(obj)
        #print("Got: [{0}]".format(rst))
        obj.Shape = rst

        #solidfacefusion = doc.addObject("Part::MultiFuse", f"{name}_solidfaces")
        #obj.Shape = Part.makeCylinder(obj.OuterRadius,20)
        #obj.Shape = s

    def determinefactor(self,obj):
        platonic_solid = platonic_solids[obj.Solid]
        radius = platonic_solid['radius']

        if obj.ActiveMeasure == "Outer radius":            
            factor = obj.OuterRadius / radius
            #print(f"Setting Outerradius: {obj.OuterRadius}")
        elif obj.ActiveMeasure == "Edge length":
            factor = obj.EdgeLength / platonic_solid['edgelength']
            #print(f"Setting edgelength: {obj.EdgeLength}")
        else:
            print("Not setting any factor [{0}]".format(obj.ActiveMeasure))
            return
        return factor

    def cylinders(self, obj, outerradius=None, edgelength=None, edgeradius=None):
        platonic_solid = platonic_solids[obj.Solid]
        factor = self.determinefactor(obj)
        #print(f"Factor: {factor} ({outerradius}) ({edgelength})")

        edgeradius = obj.EdgeRadius
        if edgeradius is None:
            edgeradius = factor*platonic_solid['edgelength']/20
            #print(f"Edgeradius redetermined at {edgeradius}")

        cylinderlist = cylindershapes(obj.Solid, factor=factor, radius=edgeradius)
        spheres = sphereshapes(obj.Solid, factor=factor, radius=edgeradius)

        objects = []

        rst = JoinAPI.connect(cylinderlist + spheres, 0)
        #if selfobj.Refine:
        rst = rst.removeSplitter()
        return rst

    def platonicsolid(self, obj,
                  edgelength=None):
        
        platonic_solid=platonic_solids[obj.Solid]

        #doc = FreeCAD.activeDocument()
        #print(doc.supportedTypes())
        radius = platonic_solid['radius']

        if obj.ActiveMeasure == "Outer radius":            
            factor = obj.OuterRadius / radius
            #print(f"Setting Outerradius: {obj.OuterRadius}")
        elif obj.ActiveMeasure == "Edge length":
            factor = obj.EdgeLength / platonic_solid['edgelength']
            #print(f"Setting edgelength: {obj.EdgeLength}")
        else:
            print("Not setting any factor [{0}]".format(obj.ActiveMeasure))
            return

        #print(f"Factor: {factor} = {factor/platonic_solid['radius']} * R")
        #print(f"Solid Edge length: {platonic_solid['edgelength']}")

        if obj.VertexPolygon:
            p = Part.makePolygon( [ normalize(x, factor) for x in platonic_solid['vertices']])
            solidwire(doc, p, name=f"{name}_vertices", radius=factor*platonic_solid['edgelength']/20)
        
        platonic_solid['edges'] = []

        if obj.Cloud:
            spheres = []
            for i, vertex in enumerate(platonic_solid['vertices']):
                s = doc.addObject("Part::Sphere", f"{name}_sphere{i}")
                s.Radius = 0.2
                p = FreeCAD.Placement()
                p.Base = FreeCAD.Vector( normalize( (vertex[0], vertex[1], vertex[2]), factor))
                s.Placement = p
                s.Visibility = False
                spheres.append(s)

            spherefusion = doc.addObject("Part::MultiFuse", f"{name}_cloud")
            spherefusion.Shapes = spheres
        
        facelist = []
        solidfaces = []
        for i, face in enumerate(platonic_solid['faces']):
            edgelist = []
            verts = platonic_solid['vertices']
            prev = None
            for v in face:
                if prev is not None:
                    edge = Part.makeLine( normalize( verts[prev], factor), normalize( verts[v], factor ))
                    edgelist.append(edge)
                prev = v
            edge = Part.makeLine( normalize( verts[prev], factor), normalize( verts[face[0]], factor) )
            edgelist.append(edge)
            wire = Part.Wire(edgelist)
            if obj.SolidOutline:
                solidfaces.append(solidwire(doc, wire, f"{name}_face{i}", radius=factor*platonic_solid['edgelength']/20))
            face = Part.Face(wire)
            facelist.append(face)

        if obj.SolidOutline:
            solidfacefusion = doc.addObject("Part::MultiFuse", f"{name}_solidfaces")
            solidfacefusion.Shapes = solidfaces

            rst = JoinAPI.connect(solidfaces, 0)
            #if selfobj.Refine:
            #    rst = rst.removeSplitter()
            return rst

        if obj.SolidObject:
            shell = Part.makeShell(facelist)
            return Part.makeSolid(shell)
            #solid = doc.addObject( "Part::Feature", name)
            #solid.Shape = Part.makeSolid(shell)


class ViewProviderPlatonicSolid:
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self, obj):
        return []

    def getIcon(self):
        return os.path.join(os.path.dirname(__file__),"simple-icosahedron.svg")

    def getDefaultDisplayModes(self):
        return "Shaded"

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        FreeCAD.ActiveDocument.recompute()

    def doubleClicked(self, obj):
        panel = PlatonicSolidPanel(obj.Object)
        panel.populate(obj.Object)
        FreeCADGui.Control.showDialog(panel)

    def __getstate__(self):
        return None

    def __setstate__(self):
        return None

def createPlatonicSolid():
    p = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'platonicSolid')
    PlatonicSolid(p)
    ViewProviderPlatonicSolid(p.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return p

class PlatonicSolidPanel:
    def __init__(self, platonic=None):
        self.form = FreeCADGui.PySideUic.loadUi(uifile)
        self.form.solid.insertItems(1, platonicobjects)
        self.form.radiustype.insertItems(1, radii)
        self.platonic = platonic

    def populate(self, obj):
        f = self.form
        if obj.ActiveMeasure == "Outer radius":
            f.radius.setValue(obj.OuterRadius)            
        elif obj.ActiveMeasure == "Edge length":
            f.radius.setValue(obj.EdgeLength)
        else:
            print("Not setting any value [{0}]".format(obj.ActiveMeasure))
            
        f.radiustype.setCurrentIndex(radii.index(obj.ActiveMeasure))
        f.solid.setCurrentIndex(platonicobjects.index(obj.Solid))
        f.vertexpolygon.setChecked(obj.VertexPolygon)
        f.cloud.setChecked(obj.Cloud)
        f.solidobject.setChecked(obj.SolidObject)
        f.edgeradius.setValue(obj.EdgeRadius)
        
    def accept(self):
        f = self.form

        solid = f.solid.currentText()
        measure = f.radiustype.currentText()
        radius = f.radius.value()
        vertexpolygon = f.vertexpolygon.isChecked()
        cloud = f.cloud.isChecked()
        solidobject = f.solidobject.isChecked()
        edgeradius = f.edgeradius.value()

        #for i in dir(f.solid):
        #    print("{0} -> [{1}]".format(i, getattr(f.solid,i)))

        #print("Solid: {0} [{1}]".format(f.solid.currentText(), f.solid.currentIndex()))

        if not self.platonic:
            self.platonic = createPlatonicSolid()

        self.platonic.Solid = solid
        self.platonic.SolidObject = solidobject
        self.platonic.VertexPolygon = vertexpolygon
        self.platonic.Cloud = cloud
        self.platonic.ActiveMeasure = measure
        self.platonic.EdgeRadius = edgeradius

        
        if measure == "Outer radius":
            self.platonic.OuterRadius = radius
            self.platonic.EdgeLength = 0
        elif measure == "Edge length":
            self.platonic.EdgeLength = radius
            self.platonic.OuterRadius = 0

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()

#panel = PlatonicSolidPanel()
#FreeCADGui.Control.showDialog(panel)                        