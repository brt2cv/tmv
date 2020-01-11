from core import g
from core.plugin.filter import Filter

from core.undo import UndoIndexError
class Undo(Filter):
    def run(self):
        try:
            im_mgr = g.get("canvas").get_container()
            im_mgr.undo()
            self.update_canvas()
        except UndoIndexError as e:
            g.call("prompt", str(e), 5)

class Redo(Filter):
    def run(self):
        try:
            im_mgr = g.get("canvas").get_container()
            im_mgr.redo()
            self.update_canvas()
        except UndoIndexError as e:
            g.call("prompt", str(e), 5)
