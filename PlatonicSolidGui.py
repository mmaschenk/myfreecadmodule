import FreeCAD,FreeCADGui
import os

from PlatonicSolidObject import PlatonicSolidPanel

class PlatonicSolidCommand:
    "A Platonic Solid"

    def GetResources(self):
        return { "MenuText": "Create Platonic Solid",
                 "ToolTip": "Create Platonic Solid",
                 "Pixmap": os.path.join(os.path.dirname(__file__),"icosahedron.svg")}

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):
        panel = PlatonicSolidPanel()
        FreeCADGui.Control.showDialog(panel)

FreeCADGui.addCommand('PlatonicSolid', PlatonicSolidCommand())

toolbar = ( "Platonic Solid", [ 'PlatonicSolid', ])