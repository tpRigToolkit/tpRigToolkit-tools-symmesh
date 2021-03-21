#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigTooklit-tools-symmesh controller implementation
"""

from __future__ import print_function, division, absolute_import

import logging

from tpRigToolkit.tools.symmesh.core import consts

logger = logging.getLogger(consts.TOOL_ID)


class SymmeshController(object):
    def __init__(self, client, model):
        super(SymmeshController, self).__init__()

        self._client = client
        self._model = model

    @property
    def client(self):
        return self._client()

    def set_global_tolerance(self, tolerance_value):
        self._model.global_tolerance = tolerance_value

    def set_operate_positive_to_negative_x_axis(self, flag):
        self._model.operate_from_positive_to_negative_x_axis = flag

    def set_use_pivot_as_origin(self, flag):
        self._model.use_pivot_as_origin = flag

    def set_revert_bias(self, value):
        self._model.revert_bias = value
        live_revert_bias = self._model.live_revert_bias
        if live_revert_bias:
            self.revert_selected_to_base()

    def set_live_revert_bias(self, flag):
        self._model.live_revert_bias = flag

    def set_base_geo_from_selection(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo:
            self.clear_selection()
            logger.warning('Select one polygon object.')
            return False

        self._model.base_geo = selected_geo
        self._model.selected_vertices = selected_vertices

        _, symmetry_table, is_symmetric = self.check_symmetry(table=True, select_asymmetric_vertices=False)
        self._model.symmetry_table = symmetry_table
        self._model.is_symmetric = is_symmetric

        return True

    def check_symmetry(self, table=True, select_asymmetric_vertices=True):
        selected_geo = self._model.base_geo
        axis = self._model.mirror_axis
        tolerance = self._model.global_tolerance
        use_pivot = self._model.use_pivot_as_origin

        return self.client.check_symmetry(
            geo=selected_geo, axis=axis, tolerance=tolerance, table=table, use_pivot=use_pivot,
            select_asymmetric_vertices=select_asymmetric_vertices)

    def select_moved_vertices(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo:
            return False

        base_geo = self._model.base_geo
        tolerance = self._model.global_tolerance

        moved_verts = self.client.select_moved_vertices(geo=selected_geo, base_geo=base_geo, tolerance=tolerance)

        return moved_verts

    def selection_mirror(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo or not selected_vertices:
            return False

        symmetry_table = self._model.symmetry_table

        if not symmetry_table:
            logger.warning('No Base Geometry Selected!')
            return selected_vertices

        mirror_vertices = self.client.selection_mirror(selected_geo, selected_vertices, symmetry_table)

        return mirror_vertices

    def mirror_selected(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo:
            return

        symmetry_table = self._model.symmetry_table
        if not symmetry_table:
            logger.warning('No Base Geometry Selected!')
            return selected_vertices

        base_geo = self._model.base_geo
        axis = self._model.mirror_axis
        tolerance = self._model.global_tolerance
        use_pivot = self._model.use_pivot_as_origin
        neg_to_pos = self._model.operate_from_positive_to_negative_x_axis

        return self.client.mirror_selected(
            geo=selected_geo, base_geo=base_geo, selected_vertices=selected_vertices, axis=axis,
            select_negative=neg_to_pos, use_pivot=use_pivot, tolerance=tolerance, flip=False,
            symmetry_table=symmetry_table)

    def flip_selected(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo:
            return

        symmetry_table = self._model.symmetry_table
        if not symmetry_table:
            logger.warning('No Base Geometry Selected!')
            return selected_vertices

        base_geo = self._model.base_geo
        axis = self._model.mirror_axis
        tolerance = self._model.global_tolerance
        use_pivot = self._model.use_pivot_as_origin
        neg_to_pos = self._model.operate_from_positive_to_negative_x_axis

        if not selected_vertices:
            selected_vertices = self.client.get_side_selected_vertices(
                geo=selected_geo, base_geo=base_geo, axis=axis, select_negative=neg_to_pos,
                use_pivot=use_pivot, tolerance=tolerance)

        return self.client.mirror_selected(
            geo=selected_geo, base_geo=base_geo, selected_vertices=selected_vertices, axis=axis,
            select_negative=neg_to_pos, use_pivot=use_pivot, tolerance=tolerance, flip=True,
            symmetry_table=symmetry_table)

    def revert_selected_to_base(self):
        selected_geo, selected_vertices = self.client.get_selected_info()
        if not selected_geo:
            return

        base_geo = self._model.base_geo
        axis = self._model.mirror_axis
        tolerance = self._model.global_tolerance
        use_pivot = self._model.use_pivot_as_origin
        revert_bias = self._model.revert_bias

        if not selected_vertices:
            selected_vertices = self.client.get_side_selected_vertices(
                geo=selected_geo, base_geo=base_geo, axis=axis, select_negative=2,
                use_pivot=use_pivot, tolerance=tolerance)

        return self.client.revert_selected_to_base(
            geo=selected_geo, base_geo=base_geo, selected_vertices=selected_vertices, bias=revert_bias)

    def clear_selection(self):
        """
        Clears selected geometry
        """

        self._model.base_geo = ''
        self._model.alt_base_geo = ''
        self._model.symmetry_table = list()
        self._model.is_symmetric = False
