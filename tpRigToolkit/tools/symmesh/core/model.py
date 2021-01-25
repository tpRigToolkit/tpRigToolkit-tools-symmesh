#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigTooklit-tools-symmesh model implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import QObject, Signal

from tpDcc.libs.python import python


class SymmeshModel(QObject):

    mirrorAxisChanged = Signal(int)
    globalToleranceChanged = Signal(float)
    operateFromPositiveToNegativeXAxisChanged = Signal(bool)
    usePivotAsOriginChanged = Signal(bool)
    baseGeoChanged = Signal(str)
    altBaseGeoChanged = Signal(str)
    symmetryTableChanged = Signal(list)
    isSymmetricChanged = Signal(bool)
    revertBiasChanged = Signal(float)
    liveRevertBiasChanged = Signal(bool)

    def __init__(self):
        super(SymmeshModel, self).__init__()

        self._mirror_axis = 0
        self._global_tolerance = 0.0010
        self._operate_from_positive_to_negative_x_axis = False
        self._use_pivot_as_origin = True
        self._base_geo = ''
        self._alt_base_geo = ''
        self._selected_vertices = list()
        self._symmetry_table = list()
        self._is_symmetric = False
        self._revert_bias = 1.0
        self._live_revert_bias = False

    @property
    def mirror_axis(self):
        return self._mirror_axis

    @mirror_axis.setter
    def mirror_axis(self, value):
        self._mirror_axis = int(value)
        self.mirrorAxisChanged.emit(self._mirror_axis)

    @property
    def global_tolerance(self):
        return self._global_tolerance

    @global_tolerance.setter
    def global_tolerance(self, value):
        self._global_tolerance = float(value)
        self.globalToleranceChanged.emit(self._global_tolerance)

    @property
    def operate_from_positive_to_negative_x_axis(self):
        return self._operate_from_positive_to_negative_x_axis

    @operate_from_positive_to_negative_x_axis.setter
    def operate_from_positive_to_negative_x_axis(self, flag):
        self._operate_from_positive_to_negative_x_axis = bool(flag)
        self.operateFromPositiveToNegativeXAxisChanged.emit(self._operate_from_positive_to_negative_x_axis)

    @property
    def use_pivot_as_origin(self):
        return self._use_pivot_as_origin

    @use_pivot_as_origin.setter
    def use_pivot_as_origin(self, flag):
        self._use_pivot_as_origin = bool(flag)
        self.usePivotAsOriginChanged.emit(self._use_pivot_as_origin)

    @property
    def base_geo(self):
        return self._base_geo

    @base_geo.setter
    def base_geo(self, value):
        self._base_geo = str(value)
        self.baseGeoChanged.emit(self._base_geo)

    @property
    def alt_base_geo(self):
        return self._alt_base_geo

    @alt_base_geo.setter
    def alt_base_geo(self, value):
        self._alt_base_geo = str(value)
        self.altBaseGeoChanged.emit(self._alt_base_geo)

    @property
    def selected_vertices(self):
        return self._selected_vertices

    @selected_vertices.setter
    def selected_vertices(self, vertices_list):
        self._selected_vertices = python.force_list(vertices_list)

    @property
    def symmetry_table(self):
        return self._symmetry_table

    @symmetry_table.setter
    def symmetry_table(self, value):
        self._symmetry_table = python.force_list(value)
        self.symmetryTableChanged.emit(self._symmetry_table)

    @property
    def is_symmetric(self):
        return self._is_symmetric

    @is_symmetric.setter
    def is_symmetric(self, flag):
        self._is_symmetric = bool(flag)
        self.isSymmetricChanged.emit(self._is_symmetric)

    @property
    def revert_bias(self):
        return self._revert_bias

    @revert_bias.setter
    def revert_bias(self, value):
        self._revert_bias = float(value)
        self.revertBiasChanged.emit(value)

    @property
    def live_revert_bias(self):
        return self._live_revert_bias

    @live_revert_bias.setter
    def live_revert_bias(self, flag):
        self._live_revert_bias = bool(flag)
        self.liveRevertBiasChanged.emit(self._live_revert_bias)
