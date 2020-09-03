#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to build symmetrical and meshes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpDcc.core import tool
from tpDcc.libs.qt.widgets import toolset

# Defines ID of the tool
TOOL_ID = 'tpRigToolkit-tools-symmesh'


class SymMeshTool(tool.DccTool, object):
    def __init__(self, *args, **kwargs):
        super(SymMeshTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'SymMesh',
            'id': 'tpRigToolkit-tools-symmesh',
            'logo': 'symmesh',
            'icon': 'symmesh',
            'tooltip': 'Tool to build symmetrical and meshes. Based on the amazing abSymMesh MEL script.',
            'tags': ['tpRigToolkit', 'mesh', 'mirror', 'flip'],
            'logger_dir': os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs', 'tools'),
            'logger_level': 'INFO',
            'is_checkable': False,
            'is_checked': False,
            'menu_ui': {'label': 'SymMesh', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'menu': [
                {'label': 'SymMesh',
                 'type': 'menu', 'children': [{'id': 'tpRigToolkit-tools-symmesh', 'type': 'tool'}]}],
            'shelf': [
                {'name': 'SymMesh',
                 'children': [{'id': 'tpRigToolkit-tools-symmesh', 'display_label': False, 'type': 'tool'}]}
            ]
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


class SymMeshToolset(toolset.ToolsetWidget, object):

    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(SymMeshToolset, self).__init__(*args, **kwargs)

    def contents(self):

        from tpRigToolkit.tools.symmesh.widgets import symmesh
        symmesh_widget = symmesh.SymMeshWidget(parent=self)

        return [symmesh_widget]
