# coding=utf-8
"""
AltArc version 1.0.0

Copyrights(c) 2021 altnoi

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""
import maya.cmds as cmds
import maya.OpenMaya as om
import xml.etree.ElementTree as gfg


class arcLib(object):
    def get_cams(self):
        cams = cmds.ls(cameras=True)
        transforms = []
        for cam in cams:
            transforms.append(cmds.listRelatives(cam, parent=True)[0])
        return transforms

    def get_project_path(self):
        path = cmds.workspace(q=True, active=True)
        return path

    def worldspace_to_imagespace(self, camera, world_point):
        """
        world spaceをimage spaceに変換する
        :param camera: str (target camera name)
        :param world_point: list (target object position)
        :return:
        """
        # レンダー解像度を取得
        res_width = cmds.getAttr('defaultResolution.width')
        res_height = cmds.getAttr('defaultResolution.height')

        sel_list = om.MSelectionList()
        sel_list.add(camera)
        dag_path = om.MDagPath()
        sel_list.getDagPath(0, dag_path)
        dag_path.extendToShape()
        cam_inv_mtx = dag_path.inclusiveMatrix().inverse()

        fn_cam = om.MFnCamera(dag_path)
        m_float_mtx = fn_cam.projectionMatrix()
        proj_mtx = om.MMatrix(m_float_mtx.matrix)

        m_point = om.MPoint(world_point[0], world_point[1], world_point[2]) * cam_inv_mtx * proj_mtx
        x = (m_point[0] / m_point[3] / 2 + 0.5) * res_width
        y = (m_point[1] / m_point[3] / 2 + 0.5) * res_height

        y = res_height - y
        return [x, y]

    def get_data(self, start, end, items, camera):
        """
        Todo: ロケーターノードかどうかチェックするルーチンの追加(ver 1.0.1にて対応予定)
        :param start: int (start frame)
        :param end: int (end frame)
        :param items: list (output items)
        :param camera: str (target camera name)
        :return:
        """
        root = gfg.Element("AltArc")
        for item in items:
            item_element = gfg.Element("contents")
            root.append(item_element)
            name_content = gfg.SubElement(item_element, "name")
            name_content.text = item
            for i in range(int(start), int(end) + 1):
                value_element = gfg.Element("value")
                item_element.append(value_element)
                cmds.currentTime(i)
                tgt_position = cmds.pointPosition(item, world=True)
                image_space = self.worldspace_to_imagespace(camera, tgt_position)
                x = str(image_space[0])
                y = str(image_space[1])

                x_element = gfg.SubElement(value_element, "x")
                x_element.text = x
                y_element = gfg.SubElement(value_element, "y")
                y_element.text = y

        tree = gfg.ElementTree(root)
        return tree

    def save_main(self, camera, path):
        """
        :param camera: str (target camera name)
        :param path: str (save path)
        :return:
        """
        selected_items = cmds.ls(selection=True)
        start_time = cmds.playbackOptions(q=True, minTime=True)
        end_time = cmds.playbackOptions(q=True, maxTime=True)

        data_buffer = self.get_data(start_time, end_time, selected_items, camera)

        with open(path, 'w') as f:
            data_buffer.write(f)
