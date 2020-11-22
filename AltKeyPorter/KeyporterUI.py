# -*- coding: utf-8 -*-
"""
Project Name: Bridges
File name: keyPorterUI.py
Licence: MIT LICENCE
Author: altnoi
Version: 1.00
Last update: 2020_11_20
"""
from PySide2 import QtWidgets, QtCore, QtGui
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import altkeyporter.KeyporterLib
# reload is only used for debugging
reload(altkeyporter.KeyporterLib)


def maya_main_window():
    main_wnd_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_wnd_ptr), QtWidgets.QWidget)


class altKeyPorterUI(QtWidgets.QDialog):
    # filter settings
    FILE_FILTERS = "Json files(*.json);;All files(*.*)"
    selected_filter = "Json files(*.json)"
    FILE_IMG_FILTERS = "image files(*.png, *.jpg);;All files(*.*)"
    selected_img_filter = "image files(*.png, *.jpg)"

    def __init__(self, parent=maya_main_window()):
        super(altKeyPorterUI, self).__init__(parent)

        self.lib = altkeyporter.KeyporterLib.keyPorterLibrary()
        self.data = altkeyporter.KeyporterLib.keyPorterData()

        # window settings
        self.setWindowTitle("AltKeyPorter ver1.0.0")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.build_ui()
        self.create_connection()

        PROJECT_DIR = cmds.workspace(q=True, active=True)
        default_save_directory = os.path.join(PROJECT_DIR, "key_data")
        self.data.save_directory = default_save_directory
        self.load_panel()

    def build_ui(self):
        """
        UIの作成をおこないます
        :return:
        """
        main_lo = QtWidgets.QVBoxLayout(self)

        # 上部側ボタン群
        save_main_lo = QtWidgets.QVBoxLayout()
        self.name_label = QtWidgets.QLabel("name")
        self.name_label.setText("<h2><strong>name</string></h2>")
        save_main_lo.addWidget(self.name_label)
        save_le_lo = QtWidgets.QHBoxLayout()
        self.name_le = QtWidgets.QLineEdit()
        save_le_lo.addWidget(self.name_le)
        save_btn_lo = QtWidgets.QVBoxLayout()
        self.save_anim_btn = QtWidgets.QPushButton("Save animation")
        self.save_pose_btn = QtWidgets.QPushButton("Save pose")
        save_btn_lo.addWidget(self.save_anim_btn)
        save_btn_lo.addWidget(self.save_pose_btn)
        save_le_lo.addLayout(save_btn_lo)
        save_main_lo.addLayout(save_le_lo)
        main_lo.addLayout(save_main_lo)

        # list widget群
        BLOCK_SIZE = 64
        BLOCK_BUFFER = 12
        self.main_list_wgt = QtWidgets.QListWidget()
        self.main_list_wgt.setViewMode(QtWidgets.QListWidget.IconMode)
        self.main_list_wgt.setIconSize(QtCore.QSize(BLOCK_SIZE, BLOCK_SIZE))
        self.main_list_wgt.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.main_list_wgt.setGridSize(QtCore.QSize(BLOCK_SIZE + BLOCK_BUFFER, BLOCK_SIZE + BLOCK_BUFFER))
        self.main_list_wgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_list_wgt.customContextMenuRequested.connect(self.on_right_click)
        main_lo.addWidget(self.main_list_wgt)

        # 下部ボタン群
        bottom_btn_lo = QtWidgets.QHBoxLayout()
        self.reflesh_btn = QtWidgets.QPushButton("Refresh")
        self.choose_fld_btn = QtWidgets.QPushButton("Choose folder")
        self.adv_mode_btn = QtWidgets.QPushButton("Advance Mode")
        bottom_btn_lo.addStretch()
        bottom_btn_lo.addWidget(self.reflesh_btn)
        bottom_btn_lo.addWidget(self.choose_fld_btn)
        bottom_btn_lo.addWidget(self.adv_mode_btn)
        main_lo.addLayout(bottom_btn_lo)

    def create_connection(self):
        """
        UIのボタン等の動作を設定します
        :return:
        """
        self.save_anim_btn.clicked.connect(lambda: self.save_trigger(0))
        self.save_pose_btn.clicked.connect(lambda: self.save_trigger(1))

        self.main_list_wgt.doubleClicked.connect(self.load_data)

        self.reflesh_btn.clicked.connect(self.load_panel)
        self.choose_fld_btn.clicked.connect(self.change_folder)
        self.adv_mode_btn.setEnabled(False)


    def on_right_click(self, pos):
        """
        iconを右クリック時の挙動の設定
        :param pos:
        :return:
        """
        menu = QtWidgets.QMenu(self)
        rename = QtWidgets.QAction("rename", self, triggered=self.rename)
        menu.addAction(rename)
        change_image = QtWidgets.QAction("change image", self, triggered=self.change_image)
        menu.addAction(change_image)
        remove = QtWidgets.QAction("remove", self, triggered=self.remove)
        menu.addAction(remove)
        menu.exec_(self.main_list_wgt.mapToGlobal(pos))

    def load_panel(self):
        """
        パネルの読み込み処理を行います
        :return:
        """
        self.main_list_wgt.clear()
        self.lib.find(self.data)
        for name in self.data.main_dict.keys():
            item = QtWidgets.QListWidgetItem(name)
            img_path = self.data.main_dict[name]["img"]
            if os.path.exists(img_path):
                icon = QtGui.QIcon(img_path)
            else:
                icon = QtGui.QIcon(os.path.join("C:\Users\kenta\Documents\maya\controllerLibrary", 'noimage.jpg'))
            item.setIcon(icon)
            self.main_list_wgt.addItem(item)

    def save_trigger(self, status):
        """
        セーブボタンを押した際の挙動を制御します
        :param status: int(0: アニメーションモード 1: ポーズモード)
        :return:
        """
        if status == 0:
            self.lib.save(self.data, self.name_le.text(), 0)
        else:
            self.lib.save(self.data, self.name_le.text(), 1)
        QtWidgets.QMessageBox.information(self, "info", "operation complete!!!")
        self.name_le.setText("")
        self.load_panel()

    def change_folder(self):
        """
        jsonファイルを保存する先を選択しkeyPorterData.save_directory
        :return:
        """
        new_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dir", self.data.save_directory)
        if new_dir:
            self.data.save_directory = new_dir
            self.load_panel()

    def rename(self):
        """
        リネーム実施時の挙動を制御します
        :return:
        """
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            text, status = QtWidgets.QInputDialog.getText(self, "new name", "name:")
            if status:
                item = self.main_list_wgt.itemFromIndex(index)
                old_name = item.text()
                item.setText(text)
                new_name = item.text()
                status = self.lib.rename(old_name, new_name, self.data)
                if status == 1:
                    item.setText(old_name)
                    QtWidgets.QMessageBox.warning(self, "Warning", "file already exists! cannot overwrite.")

                self.load_panel()

    def change_image(self):
        """
        iconの画像変更を制御します
        :return:
        """
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            item = self.main_list_wgt.itemFromIndex(index)
            tgt_name = item.text()
            tgt_path = os.path.join(self.data.save_directory, "%s.json" % tgt_name)
            img_path, self.selected_img_filter = QtWidgets.QFileDialog.getOpenFileName( self,
                                                                                        "Open image",
                                                                                        "",
                                                                                        self.FILE_IMG_FILTERS,
                                                                                        self.selected_img_filter)
            self.lib.change_image(tgt_path, img_path)
            self.load_panel()

    def remove(self):
        """
        Jsonファイルを消去します
        :return:
        """
        button_pressed = QtWidgets.QMessageBox.question(    self,
                                                            "Question",
                                                            "Would you like to DELETE this file?")
        if button_pressed == QtWidgets.QMessageBox.Yes:
            index = self.main_list_wgt.currentIndex()
            item = self.main_list_wgt.itemFromIndex(index)
            name = item.text()
            full_path = os.path.join(self.data.save_directory, "%s.json" % name)
            if os.path.exists(full_path):
                os.remove(full_path)
                self.load_panel()
        else:
            print("Cancelled")

    def load_data(self):
        """
        アニメーションの読み込みを制御します
        :return:
        """
        current_frame = cmds.currentTime(q=True)
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            item = self.main_list_wgt.itemFromIndex(index)
            tgt_name = item.text()
            tgt_path = os.path.join(self.data.save_directory, '%s.json' % tgt_name)
            self.lib.load(tgt_path)
            cmds.currentTime(current_frame, e=True, update=True)


if __name__ == '__main__':
    try:
        alt_key_porter_ui.close()
        alt_key_porter_ui.deleteLater()
    except:
        pass

    alt_key_porter_ui = altKeyPorterUI()
    alt_key_porter_ui.show()
