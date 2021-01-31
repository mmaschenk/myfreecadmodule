import FreeCAD, FreeCADGui
import os
import Part
from math import pi, floor
import numpy as np

path = os.path.dirname(__file__)

uifile = os.path.join(path,"DecoratedCylinder.ui")

def show(obj):
    stat = ""
    for x in dir(obj):
        stat = stat + "  {0} -> [{1}]".format(x, getattr(obj,x))

    return ("DecoratedCylinder[" +
            "Radius={0}".format(getattr(obj, "Radius", None)) +
            ";Thickness={0}".format(getattr(obj, "Thickness", None)) +
            ";Height={0}".format(getattr(obj, "Height", None)) +
            ";Stripes={0}".format(getattr(obj, "Stripes", None)) +
            ";Segments={0}".format(getattr(obj, "Segments", None)) +
            ";Reversed={0}".format(getattr(obj, "Reversed", None)) +
            ";Visibility={0}".format(getattr(obj, "Visibility", None)) +
            "]")


class DecoratedCylinder:

    def __init__(self, obj):
        obj.addProperty("App::PropertyLength", 
                        "Radius", 
                        "Dimensions",
                        "Inner radius of the Cylinder").Radius=2.0
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
                        "Number of circle segments").Segments=0
        obj.addProperty("App::PropertyBool", 
                        "Reversed", 
                        "Visual",
                        "Direction of segments").Reversed=False                                                                        
        self.Type = 'decoratedCylinder'
        obj.Proxy = self

    def onChanged(self, obj, prop):
        pass
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

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

                c,n = l, l+1
                if obj.Reversed:
                    c,n = n,c
                
                #print("Making line from [{0}] to [{1}] at [{2}]".format(i,nexti,l))
                #FreeCAD.Console.PrintMessage("Making line from [{0}] to [{1}] at [{2}]\n".format(i,nexti,l))
                edge1 = Part.makeLine( (x[i],y[i],layers[c]), (x[nexti],y[nexti], layers[c]) )
                edge2 = Part.makeLine( (x[nexti],y[nexti],layers[c]), (x[nextopi],y[nextopi], layers[n]) )
                edge3 = Part.makeLine( (x[nextopi],y[nextopi],layers[n]), (x[i],y[i], layers[c]) )
                wire = Part.Wire( [edge1, edge2, edge3 ])
                face = Part.Face(wire)
                facelist.append(face)

                edge1 = Part.makeLine( (x[i],y[i],layers[c]), (x[nextopi],y[nextopi], layers[n]) )
                edge2 = Part.makeLine( (x[nextopi],y[nextopi],layers[n]), (x[topi],y[topi], layers[n]) )
                edge3 = Part.makeLine( (x[topi],y[topi],layers[n]), (x[i],y[i], layers[c]) )
                wire = Part.Wire( [edge1, edge2, edge3 ])
                face = Part.Face(wire)
                facelist.append(face)

        return facelist


    def execute(self, obj):
        if obj.Segments < 1:
            return

        FreeCAD.Console.PrintMessage("Recompute Python DecoratedCylinder feature\n")
        FreeCAD.Console.PrintMessage("Current object: [{0}]\n".format(show(obj)))

        outerfaces = self.cylinderfaces(obj, obj.Radius)
        innerfaces = self.cylinderfaces(obj, obj.Radius - obj.Thickness)
        facelist = innerfaces + outerfaces
        
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

    def onChanged(self, obj, prop):
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        #FreeCAD.Console.PrintMessage("Current object: [{0}]\n".format(show(obj)))
        FreeCAD.ActiveDocument.recompute()

    def doubleClicked(self, obj):
        panel = DecoratedCylinderPanel(obj.Object)
        panel.form.radius.setValue(obj.Object.Radius)
        panel.form.thickness.setValue(obj.Object.Thickness)
        panel.form.cylheight.setValue(obj.Object.Height)
        panel.form.segments.setValue(obj.Object.Segments)
        panel.form.stripes.setValue(obj.Object.Stripes)
        panel.form.reverse.setChecked(obj.Object.Reversed)
        FreeCADGui.Control.showDialog(panel)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

class DecoratedCylinderPanel:
    def __init__(self, dc=None):
        self.form = FreeCADGui.PySideUic.loadUi(uifile)
        self.dc = dc

    def accept(self):
        radius = self.form.radius.value()
        thickness = self.form.thickness.value()
        height = self.form.cylheight.value()
        segments = self.form.segments.value()
        stripes = self.form.stripes.value()
        reverse = self.form.reverse.isChecked()
        if not self.dc:
            self.dc = createDecoratedCylinder()
        self.dc.Radius = radius
        self.dc.Thickness = thickness
        self.dc.Height = height
        self.dc.Segments = segments
        self.dc.Reversed = reverse
        self.dc.Stripes = stripes
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()


"""
print(uifile)
panel = DecoratedCylinderPanel()
FreeCADGui.Control.showDialog(panel)
"""