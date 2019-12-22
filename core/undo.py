from utils.log import getLogger
logger = getLogger(1)

class UndoCommand:
    def execute(self):
        """ 执行的操作 """
    def rollback(self):
        """ 回滚时执行的操作 """
    def exec_init(self):
        """ 仅在第一次执行时操作，包括一些特殊的初始化操作 """

class UndoIndexError(IndexError):
    """ 撤销越界 """

class UndoStack:
    # 用于存储、管理UndoCommand操作
    def __init__(self):
        Stack = list

        self.stack_undo = Stack()  # elem: UndoCommand
        self.stack_redo = Stack()

    def _debug(self):
        total = len(self.stack_undo)
        for index, undo_cmd in enumerate(self.stack_undo):
            logger.debug(f"stack memory [{index +1}/{total}] >> {undo_cmd}")

    def undo(self):
        if not self.stack_undo:
            raise UndoIndexError("已撤回至初始状态")
            # logger.warning("已撤回至初始状态")
            # return
        undo_cmd = self.stack_undo.pop()
        ret = undo_cmd.rollback()
        self.stack_redo.append(undo_cmd)
        # self._debug()
        return ret

    def redo(self):
        if not self.stack_redo:
            raise UndoIndexError("已恢复至最终状态")
            # logger.warning("已恢复至最终状态")
            # return
        redo_cmd = self.stack_redo.pop()
        ret = redo_cmd.execute()
        self.stack_undo.append(redo_cmd)
        # self._debug()
        return ret

    def commit(self, undo_cmd):
        """ 若取消提交，return True """
        self.stack_redo.clear()
        undo_cmd.exec_init()
        ret = undo_cmd.execute()
        # 将command压栈
        self.stack_undo.append(undo_cmd)
        # print(">> UndoStack 压栈: ", undo_cmd)
        return ret
