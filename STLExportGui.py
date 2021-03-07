import FreeCADGui
import FreeCAD as App
import os, math
import Mesh, MeshPart

def exportStl():
    degrees = 3
    millimeters = 0.1
    angl = degrees * math.pi/180
    
    sel = FreeCADGui.Selection.getSelection()
    numsel = len(sel)

    if numsel != 1:
        App.Console.PrintError("Cannot export to STL with multiple objects selected")
        return

    toExport = sel[0]

    if toExport.Document.FileName=="":
        App.Console.PrintError("Cannot export from unsaved document")
        return

    _dir, _name = os.path.split(toExport.Document.FileName)
    meshName = "{}-{}.stl".format(toExport.Document.Name, toExport.Name)
    meshName = os.path.join(_dir, meshName)

    shape = toExport.Shape
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=millimeters, AngularDeflection=angl, Relative=False)
    mesh.write(Filename=meshName)
    App.Console.PrintMessage("STL file generated at {}".format(meshName))


class STLExportCommand:

    def GetResources(self):
        return { "MenuText": "Export selected object as STL",
                 "ToolTip": "Export selected object as STL",
                 "Pixmap": os.path.join(os.path.dirname(__file__),"3d-printer.svg")}

    def IsActive(self):
        if App.ActiveDocument == None:
            return False
        elif len(FreeCADGui.Selection.getSelection()) == 1:
            return True
        else:
            return False

    def Activated(self):
        exportStl()

FreeCADGui.addCommand('STL', STLExportCommand())

toolbar = ( "STL", [ 'STL', ])