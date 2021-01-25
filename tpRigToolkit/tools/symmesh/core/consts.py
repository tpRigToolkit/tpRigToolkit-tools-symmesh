#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains consts definitions used by tpRigToolkit-tools-symmesh
"""

TOOL_ID = 'tpRigToolkit-tools-symmesh'

AXIS = ['YZ', 'XZ', 'XY']
MATCH_STR = 'm'
MID_OFFSET_TOLERANCE = -.0000001
MAX_PROGRESS_BAR_THRESHOLD = 800


def get_mirror_vertex_index(symmetry_table, vertex_index):
    """
    Function that uses symmetry table to return symmetrical vertex index of the given 1; -1 if failed
    :param vertex_index: int
    :return: int
    """

    mirror_index = -1

    if not symmetry_table:
        return mirror_index

    for i in range(len(symmetry_table)):
        if vertex_index == symmetry_table[i]:
            if i % 2 == 0:
                mirror_index = symmetry_table[i + 1]
            else:
                mirror_index = symmetry_table[i - 1]
            break

    return mirror_index
