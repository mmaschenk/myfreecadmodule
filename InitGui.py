import os
import FreeCAD

class MyWorkbench ( Workbench ):
    "My workbench object"

    def __init__(self):
        Modulename = 'Mark'
        IconName = 'workbench.svg'

        mylocation = os.path.join(FreeCAD.getHomePath(), 'Mod', Modulename, IconName)

        if not os.path.exists(mylocation):
            mylocation = os.path.join(FreeCAD.getUserAppDataDir(), 'Mod', Modulename, IconName)

        if not os.path.exists(mylocation):
            print("Could not find icon!")

        print("Found location: [{0}]".format(mylocation))

        self.__class__.Icon = mylocation
    MenuText = "My Workbench"
    ToolTip = "This is my extraordinary workbench"

    def GetClassName(self):
        return "Gui::PythonWorkbench"
    
    def Initialize(self):
        import PlatonicSolidGui
        self.appendToolbar(*PlatonicSolidGui.toolbar)
        self.appendMenu(*PlatonicSolidGui.toolbar)

        import DecoratedObjectsGui
        self.appendToolbar(*DecoratedObjectsGui.toolbar)
        self.appendMenu(*DecoratedObjectsGui.toolbar)

        Log ("Loading My Workbench... done\n")

    def Activated(self):
               # do something here if needed...
        Msg ("MyWorkbench.Activated()\n")

    def Deactivated(self):
               # do something here if needed...
        Msg ("MyWorkbench.Deactivated()\n")

FreeCADGui.addWorkbench(MyWorkbench)