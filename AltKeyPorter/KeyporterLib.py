# -*- coding: utf-8 -*-
"""
Project Name: Bridges
File name: keyPorterLib.py
Licence: MIT LICENCE
Author: altnoi
Version: 1.00
Last update: 2020_11_20
"""

import maya.cmds as cmds
import maya.mel
import os
import json
import re
import copy

APP_SETTINGS = {"name": "altkeyporter", "version": "1.0.0"}


class keyPorterData(object):
    """
    アニメーションのリストを集めておくためのクラスです。
    """
    def __init__(self):
        self.save_directory = ""
        self.main_dict = {}


class keyPorterLibrary(object):
    def create_directory(self, directory):
        """
        もし、フォルダーが存在しなければ作成します
        :param directory: str
        :return:
        """
        if not os.path.exists(directory):
            os.mkdir(directory)

    def save(self, data, name, mode):
        """
        キーフレームを保存します。
        :param data: keyPorterData.main_dict
        :param name: str(ファイル名)
        :param mode: num(0: アニメーションモード 1:ポーズモード)
        :return:
        """
        self.create_directory(data.save_directory)
        jsonfile = os.path.join(data.save_directory, "%s.json" % name)

        items = cmds.ls(selection=True)
        done_list = []
        attr_values = {}
        value_dict = {}

        for item in items:
            keyitems = cmds.keyframe(item, q=True, name=True)
            attr_values.clear()
            if keyitems is not None:
                for keyitem in keyitems:
                    if keyitem not in done_list:
                        if "|" in item:
                            true_item_name = item.rsplit("|", 1)[1]
                            attr_name = keyitem.replace('%s_' % true_item_name, '')
                        else:
                            attr_name = keyitem.replace('%s_' % item, '')

                        last_number = re.search(r'(?<![_\d])\d+$', attr_name)
                        if last_number is not None:
                            attr_name = attr_name.rstrip(last_number.group())

                        done_list.append(keyitem)

                        if mode == 0:
                            range_info = self.get_timeslider_range()
                            if range_info[0] + 1 == range_info[1]:
                                range_info[0] = cmds.playbackOptions(q=True, minTime=True)
                                range_info[1] = cmds.playbackOptions(q=True, maxTime=True)
                                attr_values[attr_name] = self.get_keyframe_anim(keyitem, range_info)
                        elif mode == 1:
                            current_frame = cmds.currentTime(q=True)
                            attr_values[attr_name] = self.get_keyframe_pose(item, attr_name)

            value_dict[item] = copy.copy(attr_values)

        JSON_BASE = {"imagepath": "testdir", "value": value_dict, "appsettings": APP_SETTINGS}
        with open(jsonfile, "w") as f:
            json.dump(JSON_BASE, f, indent=4)

    def get_keyframe_anim(self, keyitem, range_info):
        """
        キーフレームの情報を取得します。
        :param keyitem: str
        :param range_info: list[start, end]
        :return:
        """
        anim_dict = {}
        key_count = cmds.keyframe(keyitem, q=True, kc=True)
        for i in range(0, key_count):
            val = cmds.keyframe(keyitem, index=(i, i), vc=True, q=True)
            time = cmds.keyframe(keyitem, index=(i, i), tc=True, q=True)
            inWeight = cmds.keyTangent(keyitem, index=(i, i), inWeight=True, q=True)
            inTangent = cmds.keyTangent(keyitem, index=(i, i), inAngle=True, q=True)
            outWeight = cmds.keyTangent(keyitem, index=(i, i), outWeight=True, q=True)
            outTangent = cmds.keyTangent(keyitem, index=(i, i), outAngle=True, q=True)
            if range_info[0] <= time[0] <= range_info[1]:
                anim_dict[i] = {"time": time[0], "value": val[0], "iw": inWeight[0], "it": inTangent[0],
                                "ow": outWeight[0], "ot": outTangent[0]}

        return anim_dict

    def get_keyframe_pose(self, obj, attr):
        """
        ポーズの情報を取得します
        :param obj: str(オブジェクト名)
        :param attr: str(アトリビュート名)
        :return: anim_dict: dictionary(アニメーション情報の入った辞書を返します)
        """
        anim_dict = {}
        cmds.select(clear=True)
        cmds.select(obj)
        val = cmds.getAttr("."+attr)
        anim_dict["0"] = {"time": 0, "value": val}
        return anim_dict

    def get_timeslider_range(self):
        """
        選択されているタイムスライダーのrangeを取得します
        :return:
        """
        aTimeSlider = maya.mel.eval('$tmpVar=$gPlayBackSlider')
        time_range = cmds.timeControl(aTimeSlider, q=True, rangeArray=True)
        return time_range

    def load(self, jsonfile):
        """
        jsonファイルよりアニメーションを取り込みます
        :param jsonfile: str(jsonファイルのパス)
        :return:
        """
        current_frame = cmds.currentTime(q=True)
        if os.path.exists(jsonfile):
            with open(jsonfile, "r") as f:
                content = json.load(f)
                if content["appsettings"]["name"] == "altkeyporter":
                    for obj in content["value"]:
                        for attr in content["value"][obj]:
                            for key_index in content["value"][obj][attr]:
                                cmds.select(clear=True)
                                cmds.select(obj)
                                cmds.currentTime(content["value"][obj][attr][key_index]["time"] + current_frame, e=True, update=False)
                                value = content["value"][obj][attr][key_index]["value"]
                                c = cmds.setKeyframe(v=value, at=attr)
                                if c == 0:
                                    print obj
                                    print value
                                    print attr
                                    print "fail"
                                    print "\n"

    def rename(self, old_name, new_name, data):
        """
        名前を変更します
        :param old_name: str(変更前のファイル名)
        :param new_name: str(変更先のファイル名)
        :param data: keyPorterData.main_dict
        :return: status (成功時は0を失敗時は1を返します)
        """
        status = 0
        if not (old_name == "" or new_name == ""):
            old_fullpath = os.path.join(data.save_directory, "%s.json" % old_name)
            new_fullpath = os.path.join(data.save_directory, "%s.json" % new_name)
            if not os.path.exists(new_fullpath):
                os.rename(old_fullpath, new_fullpath)
            else:
                status = 1
            return status

    def change_image(self, json_path, img_path):
        """
        iconのファイルを変更します
        :param json_path: str(変更するファイル)
        :param img_path: str(変更先ファイルパス)
        :return:
        """
        if os.path.exists(img_path):
            content = {}
            with open(json_path, "r") as f:
                content.update(json.load(f))
                content["imagepath"] = img_path

            with open(json_path, "w") as f:
                json.dump(content, f, indent=4)

    def find(self, data):
        """
        フォルダー内のjsonファイルを列挙しkeyPorterData.dataに登録します
        :param data: keyPorterData.main_dict
        :return:
        """
        data.main_dict = {}
        if not os.path.exists(data.save_directory):
            print("Folder is not exists.")
            return

        files = os.listdir(data.save_directory)
        json_files = [f for f in files if f.endswith('.json')]

        for json_file in json_files:
            name = json_file.rsplit(".", 1)
            json_path = os.path.join(data.save_directory, json_file)
            content = {}
            with open(json_path, "r") as f:
                content.update(json.load(f))
            data.main_dict[name[0]] = {"path" : os.path.join(data.save_directory, json_file),
                                         "img"  : content["imagepath"]}
