#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to build symmetrical and meshes
"""

from __future__ import print_function, division, absolute_import

import os
import sys

from tpDcc.core import tool

from tpRigToolkit.tools.symmesh.core import consts, client, toolset


class SymMeshTool(tool.DccTool, object):

    ID = consts.TOOL_ID
    CLIENT_CLASS = client.SymmeshClient
    TOOLSET_CLASS = toolset.SymMeshToolset

    def __init__(self, *args, **kwargs):
        super(SymMeshTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'SymMesh',
            'id': cls.ID,
            'supported_dccs': {
                'maya': ['2017', '2018', '2019', '2020, 2021'],
                'max': ['2017.0', '2018.0', '2019.0', '2020.0', '2021.0']
            },
            'size': [250, 200],
            'logo': 'symmesh',
            'icon': 'symmesh',
            'tooltip': 'Tool to build symmetrical and meshes. Based on the amazing abSymMesh MEL script.',
            'tags': ['tpRigToolkit', 'mesh', 'mirror', 'flip'],
            'is_checkable': False,
            'is_checked': False,
            'menu_ui': {'label': 'SymMesh', 'load_on_startup': False, 'color': '', 'background_color': ''}
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


if __name__ == '__main__':
    import tpRigToolkit.loader
    from tpDcc.managers import tools

    tool_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    if tool_path not in sys.path:
        sys.path.append(tool_path)

    tpRigToolkit.loader.init(dev=True)

    tools.ToolsManager().launch_tool_by_id(consts.TOOL_ID)
