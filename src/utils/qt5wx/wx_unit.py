from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QCheckBox, QLineEdit,
                             QGridLayout, QGroupBox, QRadioButton, QButtonGroup,
                             QSlider, QSpinBox)

class UnitBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

    def isChecked(self):
        pass

    def get_value(self):
        pass

    def set_slot(self, func_slot):
        pass


class UnitLineEdit(UnitBase):
    def __init__(self, parent, name, val_default=0, isCheckbox=True, isChecked=False):
        super().__init__(parent)

        self.edit = QLineEdit(self)
        self.edit.setText(val_default if isinstance(val_default, str) else str(val_default))

        if isCheckbox:
            self.name = QCheckBox(name, self)
            self.name.setChecked(isChecked)
            self.edit.setEnabled(isChecked)
            self.name.stateChanged.connect(self.edit.setEnabled)
        else:
            self.name = QLabel(name, self)

        layout = QHBoxLayout(self)
        layout.addWidget(self.name)
        layout.addWidget(self.edit)

    def isChecked(self):
        if isinstance(self.name, QCheckBox):
            return self.name.isChecked()
        else:
            return True

    def set_slot(self, func_slot):
        self.edit.editingFinished.connect(func_slot)

    def get_value(self):
        text = self.get_text()
        return float(text)

    def get_text(self):
        return self.edit.text()


class UnitRadio(QGroupBox):  # UnitBase
    def __init__(self, parent, name, choices, val_init=0, choices_id=None):
        """ choices = [
            ["row0", "row0_1", "row0_2"],
            ["row1", "row1_1", "row1_2"]]
        """
        super().__init__(parent)

        self.setTitle(name)
        layout = QGridLayout(self)
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)  # 独占

        radio_id = -1
        for row, list_row in enumerate(choices):
            for column, str_item in enumerate(list_row):
                btn_radio = QRadioButton(str_item, self)
                layout.addWidget(btn_radio, row, column)
                if choices_id is None:
                    radio_id += 1
                else:
                    radio_id = choices_id[row][column]
                self.btn_group.addButton(btn_radio, radio_id)

        self.set_value(val_init)

    def set_slot(self, func_slot):
        self.btn_group.buttonClicked.connect(func_slot)

    def get_value(self):
        return self.btn_group.checkedId()  # checkedButton()

    def get_text(self):
        return self.btn_group.checkedButton().text()

    def set_value(self, index):
        self.btn_group.button(index).setChecked(True)


class UnitCheckBox(QGroupBox):  # UnitBase
    def __init__(self, parent, name, choices, val_init=0, choices_id=None):
        """ choices = [
            ["row0", "row0_1", "row0_2"],
            ["row1", "row1_1", "row1_2"]]
        """
        super().__init__(parent)

        self.setTitle(name)
        layout = QGridLayout(self)
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(False)

        radio_id = -1
        for row, list_row in enumerate(choices):
            for column, str_item in enumerate(list_row):
                btn_radio = QCheckBox(str_item, self)
                layout.addWidget(btn_radio, row, column)
                if choices_id is None:
                    radio_id += 1
                else:
                    radio_id = choices_id[row][column]
                self.btn_group.addButton(btn_radio, radio_id)

        self.set_value(val_init)

    def set_slot(self, func_slot):
        self.btn_group.buttonClicked.connect(func_slot)

    def get_value(self):
        # return self.btn_group.checkedId()  # checkedButton()
        list_ret = []
        for btn in self.btn_group.buttons():
            if btn.isChecked():
                list_ret.append(self.btn_group.id(btn))
        return list_ret

    def get_text(self):
        list_ret = []
        for btn in self.btn_group.buttons():
            if btn.isChecked():
                list_ret.append(btn.text())
        return list_ret

    def set_value(self, checked_id):
        """ checked_id: int or a list of id """
        if isinstance(checked_id, int):
            checked_id = [checked_id]
        for btn in self.btn_group.buttons():
            btn.setChecked(btn in checked_id)


class UnitSlider(UnitBase):
    def __init__(self, parent, name, val_range=None, val_default=0, showValue=True, isCheckbox=True, isChecked=False):
        super().__init__(parent)

        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)

        if isCheckbox:
            self.name = QCheckBox(name, self)
            self.name.setChecked(isChecked)
            self.slider.setEnabled(isChecked)
            self.name.stateChanged.connect(self.slider.setEnabled)
        else:
            self.name = QLabel(name, self)

        if val_range:
            self.slider.setRange(*val_range)
        self.slider.setValue(val_default)

        if showValue:
            self.label = QLabel(str(val_default), self)
            self.slider.valueChanged.connect(lambda x: self.label.setText(str(x)))

        layout = QHBoxLayout(self)
        layout.addWidget(self.name)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

    def isChecked(self):
        if isinstance(self.name, QCheckBox):
            return self.name.isChecked()
        else:
            return True

    def set_slot(self, func_slot):
        self.slider.valueChanged.connect(func_slot)

    def get_value(self):
        return self.slider.value()


class UnitSpinbox(UnitBase):
    def __init__(self, parent, name, val_range=None, val_default=0, isCheckbox=True, isChecked=False):
        super().__init__(parent)

        self.spinbox = QSpinBox(self)
        if val_range:
            self.spinbox.setRange(*val_range)
        self.spinbox.setValue(val_default)

        if isCheckbox:
            self.name = QCheckBox(name, self)
            self.name.setChecked(isChecked)
            self.spinbox.setEnabled(isChecked)
            self.name.stateChanged.connect(self.spinbox.setEnabled)
        else:
            self.name = QLabel(name, self)

        layout = QHBoxLayout(self)
        layout.addWidget(self.name)
        layout.addWidget(self.spinbox)

    def isChecked(self):
        if isinstance(self.name, QCheckBox):
            return self.name.isChecked()
        else:
            return True

    def set_slot(self, func_slot):
        self.spinbox.valueChanged.connect(func_slot)

    def get_value(self):
        return self.spinbox.value()
