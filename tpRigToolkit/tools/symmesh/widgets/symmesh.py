#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to build symmetrical and meshes
"""

from __future__ import print_function, division, absolute_import

import re
import math
import logging
import traceback

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import decorators, mathlib
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import dividers, sliders

if tp.is_maya():
    from tpDcc.dccs.maya.core import decorators as maya_decorators
    undo_decorator = maya_decorators.undo_chunk
else:
    undo_decorator = decorators.empty_decorator

LOGGER = logging.getLogger('tpRigToolkit')


class SymMeshWidget(base.BaseWidget, object):

    MATCH_STR = 'm'
    AXIS = ['YZ', 'XZ', 'XY']
    MID_OFFSET_TOLERANCE = -.0000001
    MAX_PROGRESS_BAR_THRESHOLD = 800

    def __init__(self, parent=None):

        self._base_geo = None
        self._alt_base_geo = None

        self._symmetry_table = list()

        super(SymMeshWidget, self).__init__(parent=parent)

    def ui(self):
        super(SymMeshWidget, self).ui()

        top_layout = QGridLayout()
        mirror_axis_lbl = QLabel('Mirror Axis: ')
        self._axis_radio_grp = QButtonGroup()
        self._yz_radio = QRadioButton(SymMeshWidget.AXIS[0])
        self._yz_radio.setChecked(True)
        self._xz_radio = QRadioButton(SymMeshWidget.AXIS[1])
        self._xy_radio = QRadioButton(SymMeshWidget.AXIS[2])
        self._axis_radio_grp.addButton(self._yz_radio)
        self._axis_radio_grp.addButton(self._xz_radio)
        self._axis_radio_grp.addButton(self._xy_radio)
        axis_radio_layout = QHBoxLayout()
        axis_radio_layout.setContentsMargins(2, 2, 2, 2)
        axis_radio_layout.setSpacing(2)
        axis_radio_layout.addWidget(self._yz_radio)
        axis_radio_layout.addWidget(self._xz_radio)
        axis_radio_layout.addWidget(self._xy_radio)
        axis_radio_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        global_tolerance_lbl = QLabel('Global Tolerance: ')
        self._global_tolerance_spn = QDoubleSpinBox()
        self._global_tolerance_spn.setDecimals(4)
        self._global_tolerance_spn.setValue(0.0010)
        top_layout.addWidget(mirror_axis_lbl, 0, 0, Qt.AlignRight)
        top_layout.addLayout(axis_radio_layout, 0, 1)
        top_layout.addWidget(global_tolerance_lbl, 1, 0)
        top_layout.addWidget(self._global_tolerance_spn, 1, 1)

        options_cbx_layout = QHBoxLayout()
        options_cbx_layout.setContentsMargins(2, 2, 2, 2)
        options_cbx_layout.setSpacing(2)
        self._neg_to_pox_cbx = QCheckBox('Operate -X to +X')
        self._use_pivot_as_origin_cbx = QCheckBox('Use Pivot as Origin')
        self._use_pivot_as_origin_cbx.setChecked(True)
        options_cbx_layout.addWidget(self._neg_to_pox_cbx)
        options_cbx_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        options_cbx_layout.addWidget(self._use_pivot_as_origin_cbx)
        options_cbx_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        select_geo_layout = QHBoxLayout()
        select_geo_layout.setContentsMargins(2, 2, 2, 2)
        select_geo_layout.setSpacing(2)
        self._select_geo_line = QLineEdit()
        self._select_geo_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._select_geo_line.setReadOnly(True)
        self._select_base_geo_btn = QPushButton('Select Base Geo')
        select_geo_layout.addWidget(self._select_geo_line)
        select_geo_layout.addWidget(self._select_base_geo_btn)

        self._check_symmetry_btn = QPushButton('Check Symmetry')
        self._selection_mirror_btn = QPushButton('Selection Mirror')
        self._select_moved_verts_btn = QPushButton('Select Moved Vertices')
        self._mirror_selected_btn = QPushButton('Mirror Selected')
        self._flip_selected_btn = QPushButton('Flip Selected')
        self._revert_selected_to_base = QPushButton('Revert Selected to Base')
        self._revert_slider = sliders.HoudiniDoubleSlider(parent=self, slider_range=[0.0, 1.0])

        self._selection_mirror_btn.setEnabled(False)
        self._select_moved_verts_btn.setEnabled(False)
        self._mirror_selected_btn.setEnabled(False)
        self._flip_selected_btn.setEnabled(False)
        self._revert_selected_to_base.setEnabled(False)

        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(options_cbx_layout)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addLayout(select_geo_layout)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._check_symmetry_btn)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._check_symmetry_btn)
        self.main_layout.addWidget(self._selection_mirror_btn)
        self.main_layout.addWidget(self._select_moved_verts_btn)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._mirror_selected_btn)
        self.main_layout.addWidget(self._flip_selected_btn)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._revert_selected_to_base)
        self.main_layout.addWidget(self._revert_slider)

    def setup_signals(self):
        self._axis_radio_grp.buttonToggled.connect(self._clear_selected_geo)
        self._select_base_geo_btn.clicked.connect(self._on_selected_base_geo)
        self._check_symmetry_btn.clicked.connect(self._on_check_symmetry)
        self._selection_mirror_btn.clicked.connect(self._on_selection_mirror)
        self._select_moved_verts_btn.clicked.connect(self._on_selected_moved_verts)
        self._mirror_selected_btn.clicked.connect(self._on_mirror_selected)
        self._flip_selected_btn.clicked.connect(self._on_flip_selected)
        self._revert_selected_to_base.clicked.connect(self._on_revert_selected_to_base)

    def check_symmetry(self, obj, axis, tolerance, table, use_pivot):

        pos_verts = list()
        neg_verts = list()
        pos_verts_int = list()
        neg_verts_int = list()
        pos_verts_trans = list()
        neg_verts_trans = list()
        vert_counter = 0
        non_symm_verts = list()

        axis_ind = axis
        axis_2_ind = (axis_ind + 1) % 3
        axis_3_ind = (axis_ind + 2) % 3

        if use_pivot:
            vtx_trans = tp.Dcc.node_world_space_translation(obj)
            mid = vtx_trans[axis_ind]
        else:
            if table:
                bounding_box = tp.Dcc.node_world_bounding_box(obj)
                mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)
            else:
                mid = 0

        if table:
            self._symmetry_table = list()

        total_vertices = tp.Dcc.total_vertices(obj)

        tp.Dcc.enable_wait_cursor()
        dcc_progress_bar = tp.DccProgressBar(title='Working', count=total_vertices)
        dcc_progress_bar.status('Sorting')
        mod = math.ceil(total_vertices / 50)

        try:

            for i in range(total_vertices):
                if i % mod == 0:
                    prog_num = i
                    prog = (prog_num / total_vertices) * 100.0
                    dcc_progress_bar.inc(prog)

                vtx = tp.Dcc.node_vertex_name(obj, i)
                vtx_trans = tp.Dcc.node_vertex_world_space_translation(obj, i)
                mid_offset = vtx_trans[axis_ind] - mid
                if mid_offset >= self.MID_OFFSET_TOLERANCE:
                    pos_verts.append(vtx)
                    if table:
                        pos_verts_int.append(i)
                    pos_verts_trans.append(vtx_trans[axis_ind])
                else:
                    if mid_offset < self.MID_OFFSET_TOLERANCE:
                        neg_verts.append(vtx)
                        if table:
                            neg_verts_int.append(i)
                        neg_verts_trans.append(vtx_trans[axis_ind])

            msg = 'Building Symmetry Table' if table else 'Checking for Symmetry'
            dcc_progress_bar.set_progress(0)
            dcc_progress_bar.status(msg)
            for i in range(len(pos_verts)):
                if i % mod == 0:
                    prog_num = i
                    prog = (prog_num / total_vertices) * 100.0
                    dcc_progress_bar.inc(prog)

                vtx = pos_verts[i]
                pos_offset = pos_verts_trans[i] - mid
                if pos_offset < tolerance:
                    pos_verts[i] = self.MATCH_STR
                    vert_counter += 1
                    continue

                for j in range(len(neg_verts)):
                    if neg_verts[j] == self.MATCH_STR:
                        continue
                    neg_offset = mid - neg_verts_trans[j]
                    if neg_offset < tolerance:
                        neg_verts[j] = self.MATCH_STR
                        vert_counter += 1
                        continue

                    if abs(pos_offset - neg_offset) <= tolerance:
                        vtx_trans = tp.Dcc.node_vertex_world_space_translation(vtx)
                        vtx2_trans = tp.Dcc.node_vertex_world_space_translation(neg_verts[j])
                        test1 = vtx_trans[axis_2_ind] - vtx2_trans[axis_2_ind]
                        test2 = vtx_trans[axis_3_ind] - vtx2_trans[axis_3_ind]
                        if abs(test1) < tolerance and abs(test2) < tolerance:
                            if table:
                                self._symmetry_table.append(pos_verts_int[i])
                                self._symmetry_table.append(neg_verts_int[j])
                                vert_counter += 2

                            pos_verts[i] = neg_verts[j] = self.MATCH_STR
                            break

            pos_verts = [x for x in pos_verts if x not in [self.MATCH_STR]]
            neg_verts = [x for x in neg_verts if x not in [self.MATCH_STR]]

            non_symm_verts = pos_verts + neg_verts

            if table:
                if vert_counter != total_vertices:
                    LOGGER.warning('Base geometry is not symmetrical, not all vertices can be mirrored')
                else:
                    LOGGER.info('Base geometry is symmetrical')
        except Exception as exc:
            LOGGER.error('Error while checking symmetry: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            tp.Dcc.disable_wait_cursor()
            dcc_progress_bar.end()

        return non_symm_verts

    @undo_decorator
    def selection_mirror(self, obj, selected_verts):

        if not self._symmetry_table:
            LOGGER.warning('No Base Geometry Selected!')
            return selected_verts

        tp.Dcc.enable_wait_cursor()

        mirror_vertices = list()

        try:
            for selected_vertex in selected_verts:
                vert_num = int(re.search(r'\[(\w+)\]', selected_vertex).group(1))
                mirror_vert_num = self._get_mirror_vertex_index(vert_num)
                if mirror_vert_num != -1:
                    mirror_vertices.append(tp.Dcc.node_vertex_name(obj, mirror_vert_num))
                else:
                    mirror_vertices.append(tp.Dcc.node_vertex_name(obj, vert_num))

        except Exception as exc:
            LOGGER.error('Error while selecting mirror: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            tp.Dcc.disable_wait_cursor()

        return mirror_vertices

    @undo_decorator
    def select_moved_vertices(self, obj, base_obj, tolerance):

        moved_vertices = list()

        total_vertices = tp.Dcc.total_vertices(obj)

        tp.Dcc.enable_wait_cursor()
        dcc_progress_bar = tp.DccProgressBar(title='Working', count=total_vertices)
        dcc_progress_bar.status('Checking Verts')
        mod = math.ceil(total_vertices / 50)

        try:
            for i in range(total_vertices):
                if i % mod == 0:
                    prog_num = i
                    prog = (prog_num / total_vertices) * 100.0
                    dcc_progress_bar.inc(prog)

                vtx = tp.Dcc.node_vertex_name(obj, i)
                vec1 = mathlib.Vector(*tp.Dcc.node_vertex_object_space_translation(base_obj, i))
                vec2 = mathlib.Vector(*tp.Dcc.node_vertex_object_space_translation(obj, i))

                if mathlib.get_distance_between_vectors(vec1, vec2) > tolerance:
                    moved_vertices.append(vtx)
        except Exception as exc:
            LOGGER.error('Error while selecting moving vertices: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            tp.Dcc.disable_wait_cursor()
            dcc_progress_bar.end()

        return moved_vertices

    @undo_decorator
    def mirror_selected(self, obj, base_obj, selected_verts, axis, neg_to_pos, flip, use_pivot, tolerance):

        zero_verts_int = list()
        pos_verts_int = list()
        neg_verts_int = list()

        axis_ind = axis

        total_vertices = len(selected_verts)

        if use_pivot:
            vtx_trans = tp.Dcc.node_world_space_translation(obj)
            mid = vtx_trans[axis_ind]
            vtx_trans = tp.Dcc.node_world_space_translation(base_obj)
            base_mid = vtx_trans[axis_ind]
        else:
            mid = 0
            bounding_box = tp.Dcc.node_world_bounding_box(base_obj)
            base_mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)

        show_progress = False
        tp.Dcc.enable_wait_cursor()
        if total_vertices > self.MAX_PROGRESS_BAR_THRESHOLD:
            show_progress = True
            progress_status = 'Flipping Vertices' if flip else 'Mirroring Vertices'
            dcc_progress_bar = tp.DccProgressBar(title='Working', count=total_vertices)
            dcc_progress_bar.status(progress_status)
            mod = math.ceil(total_vertices / 50)

        try:
            for i in range(total_vertices):
                if show_progress:
                    if i % mod == 0:
                        prog_num = i
                        prog = (prog_num / total_vertices) * 50.0
                        dcc_progress_bar.inc(prog)

                vtx = selected_verts[i]
                vert_num = int(re.search(r'\[(\w+)\]', vtx).group(1))
                vtx_trans = tp.Dcc.node_vertex_world_space_translation(base_obj, vert_num)
                base_mid_offset = vtx_trans[axis_ind] - base_mid
                if abs(base_mid_offset) < tolerance:
                    zero_verts_int.append(vert_num)
                    continue
                if base_mid_offset > 0:
                    pos_verts_int.append(vert_num)
                    continue
                if base_mid_offset < 0:
                    neg_verts_int.append(vert_num)
                    continue

            if neg_to_pos:
                pos_verts_int = neg_verts_int

            if show_progress:
                mod = math.ceil(len(pos_verts_int)/50)

            for i in range(len(pos_verts_int)):
                if show_progress:
                    if i % mod == 0:
                        prog_num = i
                        prog = (prog_num / total_vertices) * 50.0 + 50
                        dcc_progress_bar.inc(prog)

                vert_num = self._get_mirror_vertex_index(pos_verts_int[i])
                if vert_num != -1:
                    vtx_trans = tp.Dcc.node_vertex_world_space_translation(obj, pos_verts_int[i])
                    vtx_trans[axis_ind] = 2 * mid - vtx_trans[axis_ind]

                    if not flip:
                        tp.Dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=vert_num, translate_list=vtx_trans)
                    else:
                        flip_vtx_trans = tp.Dcc.node_vertex_world_space_translation(obj, vert_num)
                        flip_vtx_trans[axis_ind] = 2 * mid - flip_vtx_trans[axis_ind]
                        tp.Dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=vert_num, translate_list=vtx_trans)
                        tp.Dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=pos_verts_int[i], translate_list=flip_vtx_trans)

            for i in range(len(zero_verts_int)):
                vtx_trans = tp.Dcc.node_vertex_world_space_translation(obj, zero_verts_int[i])
                if flip:
                    vtx_trans[axis_ind] = 2 * mid - vtx_trans[axis_ind]
                else:
                    vtx_trans[axis_ind] = mid
                tp.Dcc.set_node_vertex_world_space_translation(
                    obj, vertex_id=zero_verts_int[i], translate_list=vtx_trans)
        except Exception as exc:
            error_msg = 'Error while flipping vertices' if flip else 'Error while mirroring vertices'
            LOGGER.error('{}: {} | {}'.format(error_msg, exc, traceback.format_exc()))
        finally:
            tp.Dcc.disable_wait_cursor()
            if show_progress:
                dcc_progress_bar.end()

    @undo_decorator
    def revert_selected_to_base(self, obj, base_obj, selected_verts, bias):

        total_vertices = len(selected_verts)

        if bias > 1:
            bias = 1
        elif bias < 0:
            bias = 0
        bias = 1 - bias
        if bias < 0.01:
            bias = 0

        show_progress = False
        tp.Dcc.enable_wait_cursor()
        if total_vertices > self.MAX_PROGRESS_BAR_THRESHOLD:
            show_progress = True
            dcc_progress_bar = tp.DccProgressBar(title='Working', count=total_vertices)
            dcc_progress_bar.status('Reverting Vertices')
            mod = math.ceil(total_vertices / 50)

        try:
            for i in range(total_vertices):
                if show_progress:
                    if i % mod == 0:
                        prog_num = i
                        prog = (prog_num / total_vertices) * 50.0 + 50
                        dcc_progress_bar.inc(prog)

                vtx = selected_verts[i]
                vert_num = int(re.search(r'\[(\w+)\]', vtx).group(1))
                obj_trans = mathlib.Vector(*tp.Dcc.node_vertex_object_space_translation(vtx))
                base_trans = mathlib.Vector(*tp.Dcc.node_vertex_object_space_translation(base_obj, vert_num))

                if mathlib.get_distance_between_vectors(obj_trans, base_trans) > 0:
                    tp.Dcc.set_node_vertex_object_space_translation(vtx, translate_list=[
                        base_trans.x + (obj_trans.x - base_trans.x) * bias,
                        base_trans.y + (obj_trans.y - base_trans.y) * bias,
                        base_trans.z + (obj_trans.z - base_trans.z) * bias,
                    ])
        except Exception as exc:
            LOGGER.error('Error while reverting vertices: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            tp.Dcc.disable_wait_cursor()
            if show_progress:
                dcc_progress_bar.end()

    def _get_selected_info(self):
        """
        Internal function that updates selected geo info (selected geometry and vertices)
        """

        nodes = tp.Dcc.selected_nodes(flatten=True)
        selected_geo = tp.Dcc.filter_nodes_by_selected_components(filter_type=12, nodes=nodes)
        selected_vertices = None
        if selected_geo:
            selected_geo = selected_geo[0]
        if not selected_geo:
            hilited_geo = tp.Dcc.selected_hilited_nodes()
            if len(hilited_geo) == 1:
                selected_geo = hilited_geo[0]
                selected_vertices = tp.Dcc.filter_nodes_by_selected_components(filter_type=31, nodes=nodes)
            elif len(hilited_geo) > 1:
                LOGGER.warning('Only one object can be hilited in component mode!')

        if not selected_geo or not tp.Dcc.object_exists(selected_geo):
            return None

        return selected_geo, selected_vertices

    def _get_mirror_vertex_index(self, vertex_index):
        """
        Internal function that uses symmetry table to return symmetrical vertex index of the given 1; -1 if failed
        :param vertex_index: int
        :return: int
        """

        mirror_index = -1

        if not self._symmetry_table:
            return mirror_index

        for i in range(len(self._symmetry_table)):
            if vertex_index == self._symmetry_table[i]:
                if i % 2 == 0:
                    mirror_index = self._symmetry_table[i + 1]
                else:
                    mirror_index = self._symmetry_table[i - 1]
                break

        return mirror_index

    def _get_side_selected_vertices(self, obj, base_obj, axis, select_negative, use_pivot, tolerance):
        """
        Internal function that selects a side of the object (located on the origin).
        This function does not uses any symmetrical data, so its faster
        :param obj: str,
        :param base_obj: str
        :param axis: int
        :param select_negative: bool or int, True selects negative side of mesh; False selects positive side of mesh;
            2 selects all vertices
        :param use_pivot: bool
        :param tolerance: float
        :return: list
        """

        side_vertices = list()

        # From (1 to 3) to (0 to 2)
        axis_ind = axis

        total_vertices = tp.Dcc.total_vertices(obj)

        if select_negative == 2:
            for i in range(total_vertices):
                vtx = tp.Dcc.node_vertex_name(obj, i)
                side_vertices.append(vtx)
            return side_vertices

        if use_pivot:
            vtx_trans = tp.Dcc.node_world_space_translation(base_obj)
            base_mid = vtx_trans[axis_ind]
        else:
            bounding_box = tp.Dcc.node_world_bounding_box(base_obj)
            base_mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)

        for i in range(total_vertices):
            vertex_name = tp.Dcc.node_vertex_name(obj, i)
            vtx_trans = tp.Dcc.node_vertex_world_space_translation(base_obj, i)
            base_mid_offset = vtx_trans[axis_ind] - base_mid
            if abs(base_mid_offset) < tolerance:
                side_vertices.append(vertex_name)
                continue
            if base_mid_offset > 0 and not select_negative:
                side_vertices.append(vertex_name)
                continue
            if base_mid_offset < 0 and select_negative:
                side_vertices.append(vertex_name)
                continue

        return side_vertices

    def _clear_selected_geo(self):
        """
        Internal function that clears selected geometry
        """

        self._base_geo = None
        self._alt_base_geo = None
        self._symmetry_table = list()
        self._selection_mirror_btn.setEnabled(False)
        self._select_moved_verts_btn.setEnabled(False)
        self._mirror_selected_btn.setEnabled(False)
        self._flip_selected_btn.setEnabled(False)
        self._revert_selected_to_base.setEnabled(False)
        self._select_geo_line.setText('')

    def _on_selected_base_geo(self):
        """
        Internal callback function that is called when Select Base Geometry button is clicked
        """

        selected_geo = self._get_selected_info()[0]
        if not selected_geo:
            self._clear_selected_geo()
            LOGGER.warning("Select one polygon object")
            return False

        tolerance = self._global_tolerance_spn.value()
        use_pivot = self._use_pivot_as_origin_cbx.isChecked()
        axis = self.AXIS.index(self._axis_radio_grp.checkedButton().text())

        self.check_symmetry(selected_geo, axis=axis, tolerance=tolerance, table=True, use_pivot=use_pivot)

        self._select_geo_line.setText(str(selected_geo))

        self._base_geo = selected_geo
        self._selection_mirror_btn.setEnabled(True)
        self._select_moved_verts_btn.setEnabled(True)
        self._mirror_selected_btn.setEnabled(True)
        self._flip_selected_btn.setEnabled(True)
        self._revert_selected_to_base.setEnabled(True)

        if tp.is_maya():
            tp.Dcc.focus_ui_panel('modelPanel1')

    def _on_check_symmetry(self):
        """
        Internal callback function that is called when Check Symmetry button is clicked
        """

        selected_geo = self._get_selected_info()[0]
        if not selected_geo:
            return False

        tolerance = self._global_tolerance_spn.value()
        use_pivot = self._use_pivot_as_origin_cbx.isChecked()
        axis = self.AXIS.index(self._axis_radio_grp.checkedButton().text())

        vertices_to_select = self.check_symmetry(
            selected_geo, axis=axis, tolerance=tolerance, table=True, use_pivot=use_pivot)

        total_vertices_to_select = len(vertices_to_select)
        if total_vertices_to_select > 0:
            tp.Dcc.enable_component_selection()
            tp.Dcc.select_object(vertices_to_select)
            LOGGER.info('{} asymmetric vert(s)'.format(total_vertices_to_select))
        else:
            tp.Dcc.select_object(selected_geo)
            LOGGER.info('{} is symmetrical'.format(selected_geo))

    def _on_selection_mirror(self):
        """
        Internal callback function that is called when Selection Mirror button is clicked
        """

        selected_mesh, selected_vertices = self._get_selected_info()
        if not selected_mesh:
            return False

        mirror_vertices = self.selection_mirror(selected_mesh, selected_vertices)
        if mirror_vertices:
            tp.Dcc.select_object(mirror_vertices)

    def _on_selected_moved_verts(self):
        """
        Internal callback function that is called when Selected Moved Verts is clicked
        """

        selected_geo = self._get_selected_info()[0]
        if not selected_geo:
            return False

        base_geo = self._base_geo
        tolerance = self._global_tolerance_spn.value()

        moved_verts = self.select_moved_vertices(selected_geo, base_obj=base_geo, tolerance=tolerance)

        if len(moved_verts) > 0:
            tp.Dcc.select_object(moved_verts)

    def _on_mirror_selected(self):
        """
        Internal callback function that is called when Mirror Selected button is clicked
        """

        selected_geo, selected_vertices = self._get_selected_info()

        base_geo = self._base_geo
        tolerance = self._global_tolerance_spn.value()
        use_pivot = self._use_pivot_as_origin_cbx.isChecked()
        axis = self.AXIS.index(self._axis_radio_grp.checkedButton().text())
        neg_to_pos = self._neg_to_pox_cbx.isChecked()

        if selected_geo:
            if not selected_vertices:
                selected_vertices = self._get_side_selected_vertices(
                    selected_geo, base_obj=base_geo, axis=axis, select_negative=neg_to_pos, use_pivot=use_pivot,
                    tolerance=tolerance)
            self.mirror_selected(
                selected_geo, base_obj=base_geo, selected_verts=selected_vertices, axis=axis, neg_to_pos=neg_to_pos,
                flip=False, use_pivot=use_pivot, tolerance=tolerance)

    def _on_flip_selected(self):
        """
        Internal callback function that is called when Flip Selected button is clicked
        """

        selected_geo, selected_vertices = self._get_selected_info()

        base_geo = self._base_geo
        tolerance = self._global_tolerance_spn.value()
        use_pivot = self._use_pivot_as_origin_cbx.isChecked()
        axis = self.AXIS.index(self._axis_radio_grp.checkedButton().text())
        neg_to_pos = self._neg_to_pox_cbx.isChecked()

        if selected_geo:
            if not selected_vertices:
                selected_vertices = self._get_side_selected_vertices(
                    selected_geo, base_obj=base_geo, axis=axis, select_negative=neg_to_pos, use_pivot=use_pivot,
                    tolerance=tolerance)
            self.mirror_selected(
                selected_geo, base_obj=base_geo, selected_verts=selected_vertices, axis=axis, neg_to_pos=neg_to_pos,
                flip=True, use_pivot=use_pivot, tolerance=tolerance)

    def _on_revert_selected_to_base(self):
        """
        Internal callback function that is called when Revert Selected to base button is clicked
        """

        selected_geo, selected_vertices = self._get_selected_info()

        base_geo = self._base_geo
        tolerance = self._global_tolerance_spn.value()
        use_pivot = self._use_pivot_as_origin_cbx.isChecked()
        axis = self.AXIS.index(self._axis_radio_grp.checkedButton().text())
        revert_bias = 1

        if selected_geo:
            if not selected_vertices:
                selected_vertices = self._get_side_selected_vertices(
                    selected_geo, base_obj=base_geo, axis=axis, select_negative=2, use_pivot=use_pivot,
                    tolerance=tolerance)
            self.revert_selected_to_base(
                selected_geo, base_obj=base_geo, selected_verts=selected_vertices, bias=revert_bias)
