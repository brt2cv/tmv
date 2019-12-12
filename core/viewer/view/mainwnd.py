from PyQt5.QtGui import QIcon
from .unit_viewer import UnitViewer

# MainWnd = UnitViewer
class MainWnd(UnitViewer):
    def __init__(self):
        super().__init__(None)
        self.setup_canvas(canvas_area=None)

        self.setWindowTitle("Remote Viewer")
        self.setWindowIcon(QIcon("plugin/viewer/res/logo.png"))
        self.resize(600, 450)
        # self.move(0, 0)

        self.setProperty("class", "bkg")  # for qss
