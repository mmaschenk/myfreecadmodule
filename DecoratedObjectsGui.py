import FreeCAD,FreeCADGui
import os

from DecoratedObjects import DecoratedCylinderPanel

class DecoratedCylinderCommand:
    "A Decorated Cylinder"

    def GetResources(self):
        return { "MenuText": "Create Decorated Cylinder",
                 "ToolTip": "Create Decorated Cylinder",
                 "Pixmap": os.path.join(os.path.dirname(__file__),"cylinder.svg")}

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):
        panel = DecoratedCylinderPanel()
        FreeCADGui.Control.showDialog(panel)

FreeCADGui.addCommand('DecoratedCylinder', DecoratedCylinderCommand())

toolbar = ( "Decorated Objects", [ 'DecoratedCylinder', ])