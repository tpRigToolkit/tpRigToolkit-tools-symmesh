#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to build symmetrical and meshes
"""

from __future__ import print_function, division, absolute_import

from tpDcc.libs.qt.widgets import toolset


class SymMeshToolset(toolset.ToolsetWidget, object):
    def __init__(self, *args, **kwargs):
        super(SymMeshToolset, self).__init__(*args, **kwargs)

    def contents(self):
        from tpRigToolkit.tools.symmesh.core import model, view, controller

        symmesh_model = model.SymmeshModel()
        symmesh_controller = controller.SymmeshController(client=self._client, model=symmesh_model)
        symmesh_view = view.SymmeshView(model=symmesh_model, controller=symmesh_controller, parent=self)

        return [symmesh_view]
