# coding=utf-8
"""
AltArc version 1.00

Copyrights(c) 2021 altnoi

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

# this is debug code
import AltArc.arcLib
reload(AltArc.arcLib)


def maya_main_window():
    """
    Mayaのメインウィンドウを取得
    :return:
    """
    main_wnd_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_wnd_ptr), QtWidgets.QWidget)


class arcMainUI(QtWidgets.QDialog):
    FILE_FILTERS = "XML(*.xml);;All Files (*.*)"
    selected_filter = "XML(*.xml)"

    # dlg_instanceでインスタンスを保持し、再度呼び出された場合はこれを使って情報を復元する
    dlg_instance = None
    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = arcMainUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(arcMainUI, self).__init__(parent)

        # 重複ウィンドーを削除する
        child_list = self.parent().children()
        for c in child_list:
            if self.__class__.__name__ == c.__class__.__name__:
                c.close()

        self.setWindowTitle("AltArc version 1.0.0")
        self.setMinimumSize(300, 120)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.lib = AltArc.arcLib.arcLib()

        self.create_widgets()
        self.create_layout()
        self.create_connection()
        self.reload_cams()

    def create_widgets(self):
        self.camera_combobox = QtWidgets.QComboBox()
        self.camera_combobox.setMinimumWidth(150)
        self.camera_pushbtn = QtWidgets.QPushButton("Reload")
        self.path_le = QtWidgets.QLineEdit()
        self.path_btn = QtWidgets.QPushButton()
        self.path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.output_btn = QtWidgets.QPushButton("Save")

    def create_layout(self):
        main_lo = QtWidgets.QVBoxLayout(self)

        camera_line = QtWidgets.QHBoxLayout()
        camera_line.addWidget(self.camera_combobox)
        camera_line.addWidget(self.camera_pushbtn)

        path_line = QtWidgets.QHBoxLayout()
        path_line.addWidget(self.path_le)
        path_line.addWidget(self.path_btn)

        form_lo = QtWidgets.QFormLayout()
        form_lo.addRow("Target Camera : ", camera_line)
        form_lo.addRow("Output Path : ", path_line)
        main_lo.addLayout(form_lo)
        main_lo.addWidget(self.output_btn)

    def create_connection(self):
        self.camera_pushbtn.clicked.connect(self.reload_cams)
        self.output_btn.clicked.connect(self.save_hook)
        self.path_btn.clicked.connect(self.save_dlg)

    def reload_cams(self):
        cams = self.lib.get_cams()
        self.camera_combobox.clear()

        for cam in cams:
            self.camera_combobox.addItem(cam)

    def save_dlg(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getSaveFileName(self, "Save File As",
                                                                                self.lib.get_project_path(),
                                                                                self.FILE_FILTERS, self.selected_filter)
        if file_path:
            self.path_le.setText(file_path)

    def save_hook(self):
        """
        Todo: pathの正当性チェックルーチン追加
        :return:
        """
        tgt_path = self.path_le.text()
        tgt_cam = self.camera_combobox.currentText()
        self.lib.save_main(tgt_cam, tgt_path)


# debug code
if __name__ == "__main__":
    ui = arcMainUI()
    ui.show()
