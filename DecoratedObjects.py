import FreeCAD, FreeCADGui
import os
import Part
from math import pi

path = os.path.dirname(__file__)

uifile = os.path.join(path,"DecoratedCylinder.ui")

class DecoratedCylinder:
    def __init__(self, obj):
        obj.addProperty("App::PropertyLength", 
                        "Radius", 
                        "Dimensions",
                        "Inner radius of the Cylinder").Radius=1.0
        obj.addProperty("App::PropertyLength", 
                        "Radius2", 
                        "Dimensions",
                        "Outer radius of the Cylinder").Radius2=1.0
        obj.addProperty("App::PropertyLength", 
                        "Height", 
                        "Dimensions",
                        "Height of the Cylinder").Height=10.0
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

    def execute(self, obj):
        FreeCAD.Console.PrintMessage("Recompute Python DecoratedCylinder feature\n")
        obj.Shape = Part.makeCylinder(obj.Radius,obj.Height)

        for i in range(obj.Segments):
            phi = pi*2*i/obj.Segments
            print(phi)

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
        panel.form.radius2.setValue(obj.Object.Radius2)
        panel.form.cylheight.setValue(obj.Object.Height)
        panel.form.segments.setValue(obj.Object.Segments)
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
        radius2 = self.form.radius2.value()
        height = self.form.cylheight.value()
        segments = self.form.segments.value()
        direction = self.form.reverse.isChecked()
        print("Radius = [{0}]".format(radius))
        if not self.dc:
            self.dc = createDecoratedCylinder()
        print("Setting to: {0}".format(self.dc))
        self.dc.Radius = radius
        self.dc.Radius2 = radius2
        self.dc.Height = height
        self.dc.Segments = segments
        self.dc.Direction = direction
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()



print(uifile)

panel = DecoratedCylinderPanel()
FreeCADGui.Control.showDialog(panel)