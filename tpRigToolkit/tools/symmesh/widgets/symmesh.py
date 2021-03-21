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

from tpDcc import dcc
from tpDcc.dcc import progressbar
from tpDcc.libs.python import mathlib
from tpDcc.libs.qt.core import base

from tpRigToolkit.tools.symmesh.core import consts


logger = logging.getLogger(consts.TOOL_ID)


class SymMeshWidget(base.BaseWidget, object):

    @dcc.undo_decorator()
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
        dcc.enable_wait_cursor()
        if total_vertices > self.MAX_PROGRESS_BAR_THRESHOLD:
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
        except Exception as exc:
            logger.error('Error while reverting vertices: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            dcc.disable_wait_cursor()
            if show_progress:
                dcc_progress_bar.end()

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
