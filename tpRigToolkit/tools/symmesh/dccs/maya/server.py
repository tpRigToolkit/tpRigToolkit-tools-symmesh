#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-tools-symmesh server implementation
"""

from __future__ import print_function, division, absolute_import

import math
import logging
import traceback

import re

from tpDcc.core import server

from tpDcc import dcc
from tpDcc.dcc import progressbar
from tpDcc.libs.python import mathlib

from tpRigToolkit.tools.symmesh.core import consts

logger = logging.getLogger(consts.TOOL_ID)


class SymmeshServer(server.DccServer, object):
    PORT = 25221

    def get_selected_info(self, data, reply):
        """
        Function that returns selected geometry info (its name and its vertices)
        :return: tuple(str, list(list(float, float, float))
        """

        nodes = dcc.selected_nodes(flatten=True)
        selected_geo = dcc.filter_nodes_by_selected_components(filter_type=12, nodes=nodes, full_path=True)
        selected_vertices = None
        if selected_geo:
            selected_geo = selected_geo[0]
        if not selected_geo:
            hilited_geo = dcc.selected_hilited_nodes(full_path=True)
            if len(hilited_geo) == 1:
                selected_geo = hilited_geo[0]
                selected_vertices = dcc.filter_nodes_by_selected_components(
                    filter_type=31, nodes=nodes, full_path=False)
            elif len(hilited_geo) > 1:
                logger.warning('Only one object can be hilited in component mode!')

        if selected_geo:
            if dcc.node_is_a_shape(selected_geo):
                selected_geo = dcc.node_parent(selected_geo, full_path=True)

        if not selected_geo or not dcc.node_exists(selected_geo):
            reply['success'] = False
            reply['result'] = '', list()
            return

        reply['success'] = True
        reply['result'] = selected_geo, selected_vertices

    def check_symmetry(self, data, reply):
        obj = data['geo']
        axis = data['axis']
        tolerance = data['tolerance']
        table = data['table']
        use_pivot = data['use_pivot']
        select_asymmetric_vertices = data['select_asymmetric_vertices']

        pos_verts = list()
        neg_verts = list()
        pos_verts_int = list()
        neg_verts_int = list()
        pos_verts_trans = list()
        neg_verts_trans = list()
        vert_counter = 0
        non_symm_verts = list()
        is_symmetric = False

        axis_ind = axis
        axis_2_ind = (axis_ind + 1) % 3
        axis_3_ind = (axis_ind + 2) % 3

        if use_pivot:
            vtx_trans = dcc.node_world_space_translation(obj)
            mid = vtx_trans[axis_ind]
        else:
            if table:
                bounding_box = dcc.node_world_bounding_box(obj)
                mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)
            else:
                mid = 0

        symmetry_table = list()

        total_vertices = dcc.total_vertices(obj)

        dcc.enable_wait_cursor()
        dcc_progress_bar = progressbar.ProgressBar(title='Working', count=total_vertices)
        dcc_progress_bar.status('Sorting')
        mod = math.ceil(total_vertices / 50)

        try:
            for i in range(total_vertices):
                if i % mod == 0:
                    prog_num = i
                    prog = (prog_num / total_vertices) * 100.0
                    dcc_progress_bar.inc(prog)

                vtx = dcc.node_vertex_name(obj, i)
                vtx_trans = dcc.node_vertex_world_space_translation(obj, i)
                mid_offset = vtx_trans[axis_ind] - mid
                if mid_offset >= consts.MID_OFFSET_TOLERANCE:
                    pos_verts.append(vtx)
                    if table:
                        pos_verts_int.append(i)
                    pos_verts_trans.append(vtx_trans[axis_ind])
                else:
                    if mid_offset < consts.MID_OFFSET_TOLERANCE:
                        neg_verts.append(vtx)
                        if table:
                            neg_verts_int.append(i)
                        neg_verts_trans.append(vtx_trans[axis_ind])

            msg = 'Building Symmetry Table' if table else 'Checking for Symmetry'
            dcc_progress_bar.set_progress(0)
            dcc_progress_bar.status(msg)
            for i in range(len(pos_verts)):
                # if i % mod == 0:
                #     prog_num = i
                #     prog = (prog_num / total_vertices) * 100.0
                #     dcc_progress_bar.inc(prog)

                vtx = pos_verts[i]
                pos_offset = pos_verts_trans[i] - mid
                if pos_offset < tolerance:
                    pos_verts[i] = consts.MATCH_STR
                    vert_counter += 1
                    continue

                for j in range(len(neg_verts)):
                    if neg_verts[j] == consts.MATCH_STR:
                        continue
                    neg_offset = mid - neg_verts_trans[j]
                    if neg_offset < tolerance:
                        neg_verts[j] = consts.MATCH_STR
                        vert_counter += 1
                        continue

                    if abs(pos_offset - neg_offset) <= tolerance:
                        vtx_trans = dcc.node_vertex_world_space_translation(vtx)
                        vtx2_trans = dcc.node_vertex_world_space_translation(neg_verts[j])
                        test1 = vtx_trans[axis_2_ind] - vtx2_trans[axis_2_ind]
                        test2 = vtx_trans[axis_3_ind] - vtx2_trans[axis_3_ind]
                        if abs(test1) < tolerance and abs(test2) < tolerance:
                            if table:
                                symmetry_table.append(pos_verts_int[i])
                                symmetry_table.append(neg_verts_int[j])
                                vert_counter += 2

                            pos_verts[i] = neg_verts[j] = consts.MATCH_STR
                            break

            pos_verts = [x for x in pos_verts if x not in [consts.MATCH_STR]]
            neg_verts = [x for x in neg_verts if x not in [consts.MATCH_STR]]
            non_symm_verts = pos_verts + neg_verts

            if table:
                if vert_counter != total_vertices:
                    logger.warning('Base geometry is not symmetrical, not all vertices can be mirrored')
                else:
                    logger.info('Base geometry is symmetrical')
                    is_symmetric = True

            reply['success'] = True
        except Exception as exc:
            logger.error('Error while checking symmetry: {} | {}'.format(exc, traceback.format_exc()))
            reply['success'] = False
        finally:
            dcc.disable_wait_cursor()
            dcc_progress_bar.end()

        if select_asymmetric_vertices:
            total_vertices_to_select = len(non_symm_verts)
            if total_vertices_to_select > 0:
                dcc.enable_component_selection()
                dcc.select_node(non_symm_verts)
                logger.info('{} asymmetric vert(s)'.format(total_vertices_to_select))
            else:
                dcc.select_node(obj)

        reply['result'] = non_symm_verts, symmetry_table, is_symmetric

    @dcc.undo_decorator()
    def select_moved_vertices(self, data, reply):

        obj = data['geo']
        base_obj = data['base_geo']
        tolerance = data['tolerance']

        moved_vertices = list()

        total_vertices = dcc.total_vertices(obj)

        dcc_progress_bar = progressbar.ProgressBar(title='Working', count=total_vertices)
        dcc_progress_bar.status('Checking Verts')
        mod = math.ceil(total_vertices / 50)

        dcc.enable_wait_cursor()
        try:
            for i in range(total_vertices):
                if i % mod == 0:
                    prog_num = i
                    prog = (prog_num / total_vertices) * 100.0
                    dcc_progress_bar.inc(prog)

                vtx = dcc.node_vertex_name(obj, i)
                vec1 = mathlib.Vector(*dcc.node_vertex_object_space_translation(base_obj, i))
                vec2 = mathlib.Vector(*dcc.node_vertex_object_space_translation(obj, i))

                if mathlib.get_distance_between_vectors(vec1, vec2) > tolerance:
                    moved_vertices.append(vtx)

            if len(moved_vertices) > 0:
                dcc.select_node(obj)
                dcc.enable_component_selection()
                dcc.select_node(moved_vertices, replace_selection=False)

            reply['success'] = True

        except Exception as exc:
            logger.error('Error while selecting moving vertices: {} | {}'.format(exc, traceback.format_exc()))
            reply['success'] = False
        finally:
            dcc.disable_wait_cursor()
            dcc_progress_bar.end()

        reply['result'] = moved_vertices

    @dcc.undo_decorator()
    def selection_mirror(self, data, reply):

        selected_geo = data['geo']
        selected_vertices = data['selected_vertices']
        symmetry_table = data['symmetry_table']

        mirror_vertices = list()

        dcc.enable_wait_cursor()
        try:
            for selected_vertex in selected_vertices:
                vert_num = int(re.search(r'\[(\w+)\]', selected_vertex).group(1))
                mirror_vert_num = consts.get_mirror_vertex_index(symmetry_table, vert_num)
                if mirror_vert_num != -1:
                    mirror_vertices.append(dcc.node_vertex_name(selected_geo, mirror_vert_num))
                else:
                    mirror_vertices.append(dcc.node_vertex_name(selected_geo, vert_num))

            if mirror_vertices:
                dcc.select_node(mirror_vertices)

            reply['success'] = True

        except Exception as exc:
            logger.error('Error while selecting mirror: {} | {}'.format(exc, traceback.format_exc()))
            reply['success'] = False
        finally:
            dcc.disable_wait_cursor()

        reply['result'] = mirror_vertices

    def get_side_selected_vertices(self, data, reply):
        """
        Function that selects a side of the object (located on the origin).
        This function does not uses any symmetrical data, so its faster
        """

        obj = data['geo']
        base_obj = data['base_geo']
        axis = data['axis']
        select_negative = data['select_negative']
        use_pivot = data['use_pivot']
        tolerance = data['tolerance']

        side_vertices = list()

        # From (1 to 3) to (0 to 2)
        axis_ind = axis

        total_vertices = dcc.total_vertices(obj)

        reply['success'] = True

        if select_negative == 2:
            for i in range(total_vertices):
                vtx = dcc.node_vertex_name(obj, i)
                side_vertices.append(vtx)
                reply['result'] = side_vertices
                return

        if use_pivot:
            vtx_trans = dcc.node_world_space_translation(base_obj)
            base_mid = vtx_trans[axis_ind]
        else:
            bounding_box = dcc.node_world_bounding_box(base_obj)
            base_mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)

        for i in range(total_vertices):
            vertex_name = dcc.node_vertex_name(obj, i)
            vtx_trans = dcc.node_vertex_world_space_translation(base_obj, i)
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

        reply['result'] = side_vertices

    @dcc.undo_decorator()
    def mirror_selected(self, data, reply):

        obj = data['geo']
        base_obj = data['base_geo']
        selected_verts = data['selected_vertices']
        axis = data['axis']
        neg_to_pos = data['neg_to_pos']
        use_pivot = data['use_pivot']
        tolerance = data['tolerance']
        flip = data['flip']
        symmetry_table = data['symmetry_table']

        zero_verts_int = list()
        pos_verts_int = list()
        neg_verts_int = list()

        axis_ind = axis

        if not selected_verts:
            reply['success'] = False
            reply['msg'] = 'No vertices selected'
            return

        total_vertices = len(selected_verts)

        if use_pivot:
            vtx_trans = dcc.node_world_space_translation(obj)
            mid = vtx_trans[axis_ind]
            vtx_trans = dcc.node_world_space_translation(base_obj)
            base_mid = vtx_trans[axis_ind]
        else:
            mid = 0
            bounding_box = dcc.node_world_bounding_box(base_obj)
            base_mid = bounding_box[axis_ind] + ((bounding_box[axis_ind + 3] - bounding_box[axis_ind]) / 2)

        show_progress = False
        dcc.enable_wait_cursor()
        if total_vertices > consts.MAX_PROGRESS_BAR_THRESHOLD:
            show_progress = True
            progress_status = 'Flipping Vertices' if flip else 'Mirroring Vertices'
            dcc_progress_bar = progressbar.ProgressBar(title='Working', count=total_vertices)
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
                vtx_trans = dcc.node_vertex_world_space_translation(base_obj, vert_num)
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
                mod = math.ceil(len(pos_verts_int) / 50)

            for i in range(len(pos_verts_int)):
                if show_progress:
                    if i % mod == 0:
                        prog_num = i
                        prog = (prog_num / total_vertices) * 50.0 + 50
                        dcc_progress_bar.inc(prog)

                vert_num = consts.get_mirror_vertex_index(symmetry_table, pos_verts_int[i])
                if vert_num != -1:
                    vtx_trans = dcc.node_vertex_world_space_translation(obj, pos_verts_int[i])
                    vtx_trans[axis_ind] = 2 * mid - vtx_trans[axis_ind]

                    if not flip:
                        dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=vert_num, translate_list=vtx_trans)
                    else:
                        flip_vtx_trans = dcc.node_vertex_world_space_translation(obj, vert_num)
                        flip_vtx_trans[axis_ind] = 2 * mid - flip_vtx_trans[axis_ind]
                        dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=vert_num, translate_list=vtx_trans)
                        dcc.set_node_vertex_world_space_translation(
                            obj, vertex_id=pos_verts_int[i], translate_list=flip_vtx_trans)

            for i in range(len(zero_verts_int)):
                vtx_trans = dcc.node_vertex_world_space_translation(obj, zero_verts_int[i])
                if flip:
                    vtx_trans[axis_ind] = 2 * mid - vtx_trans[axis_ind]
                else:
                    vtx_trans[axis_ind] = mid
                dcc.set_node_vertex_world_space_translation(
                    obj, vertex_id=zero_verts_int[i], translate_list=vtx_trans)

            reply['success'] = True
        except Exception as exc:
            error_msg = 'Error while flipping vertices' if flip else 'Error while mirroring vertices'
            logger.error('{}: {} | {}'.format(error_msg, exc, traceback.format_exc()))
            reply['success'] = False
        finally:
            dcc.disable_wait_cursor()
            if show_progress:
                dcc_progress_bar.end()

    @dcc.undo_decorator()
    def revert_selected_to_base(self, data, reply):
        geo = data['geo']
        base_obj = data['base_geo']
        selected_verts = data['selected_vertices']
        bias = data['bias']

        total_vertices = len(selected_verts)

        if bias > 1:
            bias = 1
        elif bias < 0:
            bias = 0
        bias = 1 - bias
        if bias < 0.01:
            bias = 0

        show_progress = False
        dcc.enable_wait_cursor()
        if total_vertices > consts.MAX_PROGRESS_BAR_THRESHOLD:
            show_progress = True
            dcc_progress_bar = progressbar.ProgressBar(title='Working', count=total_vertices)
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
                obj_trans = mathlib.Vector(*dcc.node_vertex_object_space_translation(vtx))
                base_trans = mathlib.Vector(*dcc.node_vertex_object_space_translation(base_obj, vert_num))

                if mathlib.get_distance_between_vectors(obj_trans, base_trans) > 0:
                    dcc.set_node_vertex_object_space_translation(vtx, translate_list=[
                        base_trans.x + (obj_trans.x - base_trans.x) * bias,
                        base_trans.y + (obj_trans.y - base_trans.y) * bias,
                        base_trans.z + (obj_trans.z - base_trans.z) * bias,
                    ])
            reply['success'] = True
        except Exception as exc:
            reply['success'] = False
            logger.error('Error while reverting vertices: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            dcc.disable_wait_cursor()
            if show_progress:
                dcc_progress_bar.end()
