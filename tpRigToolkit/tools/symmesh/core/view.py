#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigTooklit-tools-symmesh view implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import Qt
from Qt.QtWidgets import QSizePolicy, QWidget, QButtonGroup, QSpacerItem

from tpDcc.managers import resources
from tpDcc.libs.qt.core import base, contexts as qt_contexts
from tpDcc.libs.qt.widgets import layouts, label, buttons, checkbox, lineedit, dividers, sliders, spinbox, message

from tpRigToolkit.tools.symmesh.core import consts


class SymmeshView(base.BaseWidget):
    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(SymmeshView, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(SymmeshView, self).ui()

        top_layout = layouts.GridLayout()
        mirror_axis_lbl = label.BaseLabel('Mirror Axis: ', parent=self)
        self._axis_radio_grp = QButtonGroup()
        self._yz_radio = buttons.BaseRadioButton(consts.AXIS[0], parent=self)
        self._xz_radio = buttons.BaseRadioButton(consts.AXIS[1], parent=self)
        self._xy_radio = buttons.BaseRadioButton(consts.AXIS[2], parent=self)
        self._radios = [self._yz_radio, self._xz_radio, self._xy_radio]
        self._axis_radio_grp.addButton(self._yz_radio)
        self._axis_radio_grp.addButton(self._xz_radio)
        self._axis_radio_grp.addButton(self._xy_radio)
        axis_radio_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        axis_radio_layout.addWidget(self._yz_radio)
        axis_radio_layout.addWidget(self._xz_radio)
        axis_radio_layout.addWidget(self._xy_radio)
        axis_radio_layout.addStretch()
        global_tolerance_lbl = label.BaseLabel('Global Tolerance: ', parent=self)
        self._global_tolerance_spn = spinbox.BaseDoubleSpinBox(parent=self)
        self._global_tolerance_spn.setDecimals(4)
        self._global_tolerance_spn.setValue(0.0010)
        top_layout.addWidget(mirror_axis_lbl, 0, 0, Qt.AlignRight)
        top_layout.addLayout(axis_radio_layout, 0, 1)
        top_layout.addWidget(global_tolerance_lbl, 1, 0)
        top_layout.addWidget(self._global_tolerance_spn, 1, 1)

        options_cbx_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        self._neg_to_pos_cbx = checkbox.BaseCheckBox('Operate -X to +X', parent=self)
        self._use_pivot_as_origin_cbx = checkbox.BaseCheckBox('Use Pivot as Origin', parent=self)
        self._use_pivot_as_origin_cbx.setChecked(True)
        options_cbx_layout.addWidget(self._neg_to_pos_cbx)
        options_cbx_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        options_cbx_layout.addWidget(self._use_pivot_as_origin_cbx)
        options_cbx_layout.addStretch()

        select_geo_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        self._select_geo_line = lineedit.BaseLineEdit(parent=self)
        self._select_geo_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._select_geo_line.setReadOnly(True)
        self._select_base_geo_btn = buttons.BaseButton('Select Base Geo', parent=self)
        self._select_base_geo_btn.setIcon(resources.icon('cursor'))
        select_geo_layout.addWidget(self._select_geo_line)
        select_geo_layout.addWidget(self._select_base_geo_btn)
        self._symmetry_message = message.BaseMessage('', parent=self).small()

        selection_widget = QWidget(parent=self)
        selection_layout = layouts.FlowLayout()
        selection_widget.setLayout(selection_layout)
        mirror_flip_widget = QWidget(parent=self)
        mirror_flip_layout = layouts.FlowLayout()
        mirror_flip_widget.setLayout(mirror_flip_layout)
        revert_widget = QWidget(parent=self)
        revert_layout = layouts.FlowLayout()
        revert_widget.setLayout(revert_layout)

        self._check_symmetry_btn = buttons.BaseButton('Check Symmetry', parent=self)
        self._selection_mirror_btn = buttons.BaseButton('Selection Mirror', parent=self)
        self._select_moved_vertices_btn = buttons.BaseButton('Select Moved Vertices', parent=self)
        self._mirror_selected_btn = buttons.BaseButton('Mirror Selected', parent=self)
        self._flip_selected_btn = buttons.BaseButton('Flip Selected', parent=self)
        self._revert_selected_to_base = buttons.BaseButton('Revert Selected to Base', parent=self)
        self._revert_bias_slider = sliders.HoudiniDoubleSlider(parent=self, slider_range=[0.0, 1.0])

        # TODO: Implement this feature
        self._live_revert_bias_cbx = checkbox.BaseCheckBox('Live', parent=self)
        self._live_revert_bias_cbx.setVisible(False)

        self._check_symmetry_btn.setIcon(resources.icon('refresh'))
        self._selection_mirror_btn.setIcon(resources.icon('vertex'))
        self._select_moved_vertices_btn.setIcon(resources.icon('cursor'))
        self._mirror_selected_btn.setIcon(resources.icon('mirror'))
        self._flip_selected_btn.setIcon(resources.icon('flip_vertical'))
        self._revert_selected_to_base.setIcon(resources.icon('rollback'))

        selection_layout.addWidget(self._check_symmetry_btn)
        selection_layout.addWidget(self._selection_mirror_btn)
        selection_layout.addWidget(self._select_moved_vertices_btn)
        mirror_flip_layout.addWidget(self._mirror_selected_btn)
        mirror_flip_layout.addWidget(self._flip_selected_btn)
        revert_layout.addWidget(self._revert_selected_to_base)
        revert_layout.addWidget(self._revert_bias_slider)
        revert_layout.addWidget(self._live_revert_bias_cbx)

        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(options_cbx_layout)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addLayout(select_geo_layout)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addWidget(self._symmetry_message)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addWidget(selection_widget)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addWidget(mirror_flip_widget)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addWidget(revert_widget)
        self.main_layout.addStretch()

    def setup_signals(self):
        self._axis_radio_grp.buttonToggled.connect(self._controller.clear_selection)
        self._global_tolerance_spn.valueChanged.connect(self._controller.set_global_tolerance)
        self._select_base_geo_btn.clicked.connect(self._controller.set_base_geo_from_selection)
        self._neg_to_pos_cbx.toggled.connect(self._controller.set_operate_positive_to_negative_x_axis)
        self._use_pivot_as_origin_cbx.toggled.connect(self._controller.set_use_pivot_as_origin)
        self._check_symmetry_btn.clicked.connect(self._controller.check_symmetry)
        self._selection_mirror_btn.clicked.connect(self._controller.selection_mirror)
        self._select_moved_vertices_btn.clicked.connect(self._controller.select_moved_vertices)
        self._mirror_selected_btn.clicked.connect(self._controller.mirror_selected)
        self._flip_selected_btn.clicked.connect(self._controller.flip_selected)
        self._revert_selected_to_base.clicked.connect(self._controller.revert_selected_to_base)
        self._revert_bias_slider.valueChanged.connect(self._controller.set_revert_bias)
        self._live_revert_bias_cbx.toggled.connect(self._controller.set_live_revert_bias)

        self._model.globalToleranceChanged.connect(self._on_global_tolerance_changed)
        self._model.operateFromPositiveToNegativeXAxisChanged.connect(
            self._on_operate_positive_to_negative_x_axis_changed)
        self._model.usePivotAsOriginChanged.connect(self._on_use_pivot_as_origin_changed)
        self._model.baseGeoChanged.connect(self._on_base_geo_changed)
        self._model.revertBiasChanged.connect(self._on_revert_bias_changed)
        self._model.liveRevertBiasChanged.connect(self._on_live_revert_bias_changed)
        self._model.isSymmetricChanged.connect(self._on_refresh_symmetric_message)

    def refresh(self):
        self._radios[self._model.mirror_axis].setChecked(True)
        self._global_tolerance_spn.setValue(self._model.global_tolerance)
        self._neg_to_pos_cbx.setChecked(self._model.operate_from_positive_to_negative_x_axis)
        self._use_pivot_as_origin_cbx.setChecked(self._model.use_pivot_as_origin)
        self._select_geo_line.setText(self._model.base_geo)
        self._revert_bias_slider.set_value(self._model.revert_bias)
        self._on_refresh_symmetric_message(self._model.is_symmetric)

    def _on_base_geo_changed(self, geo_name):
        """
        Internal callbaack function that is called when the selected model is updated in the model
        :param geo_name: str, name of the selected geometry
        """

        short_geo_name = self._controller.client.node_short_name(geo_name)
        self._select_geo_line.setText(short_geo_name)

        enabled = bool(geo_name)
        self._check_symmetry_btn.setEnabled(enabled)
        self._selection_mirror_btn.setEnabled(enabled)
        self._select_moved_vertices_btn.setEnabled(enabled)
        self._mirror_selected_btn.setEnabled(enabled)
        self._flip_selected_btn.setEnabled(enabled)
        self._revert_selected_to_base.setEnabled(enabled)

    def _on_global_tolerance_changed(self, tolerance_value):
        """
        Internal callback function that is called when global tolerance value is updated in the model
        :param tolerance_value: float, global tolerance value used to check symmetry of the geometry
        """

        with qt_contexts.block_signals(self._model):
            self._global_tolerance_spn.setValue(tolerance_value)

    def _on_operate_positive_to_negative_x_axis_changed(self, flag):
        """
        Internal callback function that is called when operate positive ot negate x axis flag changes in the model
        :param flag: bool
        """

        with qt_contexts.block_signals(self._model):
            self._neg_to_pos_cbx.setChecked(flag)

    def _on_use_pivot_as_origin_changed(self, flag):
        """
        Internal callback function that is called when use pivot as origin flag changes in the model
        :param flag: bool
        """

        with qt_contexts.block_signals(self._model):
            self._use_pivot_as_origin_cbx.setChecked(flag)

    def _on_revert_bias_changed(self, value):
        """
        Internal callback function that is called when revert bias value changes in the model
        :param value: float, value that sets how much the revert to base geo should be applied to selected vertices
        """

        with qt_contexts.block_signals(self._model):
            self._revert_bias_slider.set_value(value)

    def _on_live_revert_bias_changed(self, flag):
        """
        Internal callback function that is called when live revert bias flag changes in the model
        :param flag: bool, Whether or not revert bias should be applied while its value changes
        """

        with qt_contexts.block_signals(self._model):
            self._live_revert_bias_cbx.setChecked(flag)

    def _on_refresh_symmetric_message(self, flag):
        selected_geo = self._model.base_geo

        if not selected_geo:
            msg = 'Select Base geometry please'
            theme_type = message.MessageTypes.INFO
        else:
            if flag:
                msg = 'Base geometry is symmetrical'
                theme_type = message.MessageTypes.SUCCESS
            else:
                msg = 'Base geometry is not symmetrical'
                theme_type = message.MessageTypes.WARNING

        self._symmetry_message.text = msg
        self._symmetry_message.theme_type = theme_type
