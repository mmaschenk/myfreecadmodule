import FreeCAD, FreeCADGui
import os
import Part
from math import pi, floor
import numpy as np

path = os.path.dirname(__file__)

uifile = os.path.join(path,"DecoratedCylinder.ui")

class DecoratedCylinder:
    def __init__(self, obj):
        obj.addProperty("App::PropertyLength", 
                        "Radius", 
                        "Dimensions",
                        "Inner radius of the Cylinder").Radius=1.0
        obj.addProperty("App::PropertyLength", 
                        "Thickness", 
                        "Dimensions",
                        "Outer radius of the Cylinder").Thickness=1.0
        obj.addProperty("App::PropertyLength", 
                        "Height", 
                        "Dimensions",
                        "Height of the Cylinder").Height=10.0
        obj.addProperty("App::PropertyInteger", 
                        "Stripes", 
                        "Visual",
                        "Number of vertical segments").Stripes=5
        obj.addProperty("App::PropertyInteger", 
                        "Segments", 
                        "Visual",
                        "Number of circle segments").Segments=5
        obj.addProperty("App::PropertyBool", 
                        "Direction", 
                        "Visual",
                        "Direction of segments").Direction=True                                                                        
        self.Type = 'decoratedCylinder'
        obj.Proxy = self

    def onChanged(self, fp, prop):
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def layerpoints(self,obj,layer,radius):
        angles = np.arange(obj.Segments+1)*pi*2/obj.Segments
        x = np.sin(angles)*radius
        y = np.cos(angles)*radius
        
        return x, y
        
    def cylinderfaces(self, obj, radius):
        layers = np.arange(obj.Stripes+1)*obj.Height/obj.Stripes
        x, y = self.layerpoints(obj,1, radius)

        facelist = []
        for l in range(obj.Stripes):
            for i in range(obj.Segments):

                nexti = (i+1) % obj.Segments
                topi = (i+1) % obj.Segments
                nextopi = (topi+1) % obj.Segments
                
                print("Making line from [{0}] to [{1}]".format(i,nexti))
                edge1 = Part.makeLine( (x[i],y[i],layers[l]), (x[nexti],y[nexti], layers[l]) )
                edge2 = Part.makeLine( (x[nexti],y[nexti],layers[l]), (x[nextopi],y[nextopi], layers[l+1]) )
                edge3 = Part.makeLine( (x[nextopi],y[nextopi],layers[l+1]), (x[i],y[i], layers[l]) )
                wire = Part.Wire( [edge1, edge2, edge3 ])
                face = Part.Face(wire)
                facelist.append(face)

                edge1 = Part.makeLine( (x[i],y[i],layers[l]), (x[nextopi],y[nextopi], layers[l+1]) )
                edge2 = Part.makeLine( (x[nextopi],y[nextopi],layers[l+1]), (x[topi],y[topi], layers[l+1]) )
                edge3 = Part.makeLine( (x[topi],y[topi],layers[l+1]), (x[i],y[i], layers[l]) )
                wire = Part.Wire( [edge1, edge2, edge3 ])
                face = Part.Face(wire)
                facelist.append(face)

        return facelist


    def execute(self, obj):
        FreeCAD.Console.PrintMessage("Recompute Python DecoratedCylinder feature\n")

        facelist = self.cylinderfaces(obj, obj.Radius) + self.cylinderfaces(obj, obj.Radius - obj.Thickness)

        outerx, outery = self.layerpoints(obj, 1, obj.Radius)
        innerx, innery = self.layerpoints(obj, 1, obj.Radius - obj.Thickness)

        layers = np.arange(obj.Stripes+1)*obj.Height/obj.Stripes
        for l in [ 0, obj.Height]:
            for p in range(obj.Segments):
                edge1 = Part.makeLine( (outerx[p],outery[p],l), (outerx[p+1],outery[p+1],l) )
                edge2 = Part.makeLine( (outerx[p+1],outery[p+1],l), (innerx[p+1],innery[p+1],l) )
                edge3 = Part.makeLine( (innerx[p+1],innery[p+1],l), (innerx[p],innery[p],l) )
                edge4 = Part.makeLine( (innerx[p],innery[p],l), (outerx[p],outery[p],l) )
                wire = Part.Wire( [edge1, edge2, edge3, edge4 ])
                face = Part.Face(wire)
                facelist.append(face)

        shell = Part.makeShell(facelist)
        solid = Part.makeSolid(shell)
        obj.Shape = solid.removeSplitter()

def createDecoratedCylinder():
    cyl = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'decoratedCylinder')
    DecoratedCylinder(cyl)
    ViewProviderDecoratedCylinder(cyl.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    
    return cyl

class ViewProviderDecoratedCylinder:
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self, obj):
        return []

    def getDefaultDisplayModes(self):
        return "Shaded"

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        FreeCAD.ActiveDocument.recompute()

    def doubleClicked(self, obj):
        panel = DecoratedCylinderPanel(obj.Object)
        panel.form.radius.setValue(obj.Object.Radius)
        panel.form.thickness.setValue(obj.Object.Thickness)
        print("Sett it")
        panel.form.cylheight.setValue(obj.Object.Height)
        panel.form.segments.setValue(obj.Object.Segments)
        panel.form.stripes.setValue(obj.Object.Stripes)
        panel.form.reverse.setChecked(obj.Object.Direction)
        FreeCADGui.Control.showDialog(panel)

    def __getstate__(self):
        return None

    def __setstate__(self):
        return None

class DecoratedCylinderPanel:
    def __init__(self, dc=None):
        self.form = FreeCADGui.PySideUic.loadUi(uifile)
        self.dc = dc

    def accept(self):
        print("Accepting")

        for i in dir(self.form):
            print("{0} -> [{1}".format(i,getattr(self.form,i)))

        radius = self.form.radius.value()
        thickness = self.form.thickness.value()
        height = self.form.cylheight.value()
        segments = self.form.segments.value()
        stripes = self.form.stripes.value()
        direction = self.form.reverse.isChecked()
        print("Radius = [{0}]".format(radius))
        if not self.dc:
            self.dc = createDecoratedCylinder()
        print("Setting to: {0}".format(self.dc))
        self.dc.Radius = radius
        self.dc.Thickness = thickness
        self.dc.Height = height
        self.dc.Segments = segments
        self.dc.Direction = direction
        self.dc.Stripes = stripes
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()



print(uifile)

panel = DecoratedCylinderPanel()
FreeCADGui.Control.showDialog(panel)