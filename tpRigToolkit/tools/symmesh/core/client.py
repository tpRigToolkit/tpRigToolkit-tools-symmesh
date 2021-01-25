#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-tools-symmesh client implementation
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import client


class SymmeshClient(client.DccClient, object):

    PORT = 25221

    def get_selected_info(self):
        cmd = {
            'cmd': 'get_selected_info'
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return ['', list()]

        return reply_dict['result']

    def check_symmetry(self, geo, axis, tolerance, table, use_pivot, select_asymmetric_vertices):
        cmd = {
            'cmd': 'check_symmetry',
            'geo': geo,
            'axis': axis,
            'tolerance': tolerance,
            'table': table,
            'use_pivot': use_pivot,
            'select_asymmetric_vertices': select_asymmetric_vertices
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list(), list(), False

        return reply_dict['result']

    def select_moved_vertices(self, geo, base_geo, tolerance):
        cmd = {
            'cmd': 'select_moved_vertices',
            'geo': geo,
            'base_geo': base_geo,
            'tolerance': tolerance
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['result']

    def selection_mirror(self, geo, vertices, symmetry_table):
        cmd = {
            'cmd': 'selection_mirror',
            'geo': geo,
            'selected_vertices': vertices,
            'symmetry_table': symmetry_table
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['result']

    def get_side_selected_vertices(self, geo, base_geo, axis, select_negative, use_pivot, tolerance):
        cmd = {
            'cmd': 'get_side_selected_vertices',
            'geo': geo,
            'base_geo': base_geo,
            'axis': axis,
            'select_negative': select_negative,
            'use_pivot': use_pivot,
            'tolerance': tolerance,
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['result']

    def mirror_selected(
            self, geo, base_geo, selected_vertices, axis, select_negative, use_pivot, tolerance, flip, symmetry_table):
        cmd = {
            'cmd': 'mirror_selected',
            'geo': geo,
            'base_geo': base_geo,
            'selected_vertices': selected_vertices,
            'axis': axis,
            'neg_to_pos': select_negative,
            'use_pivot': use_pivot,
            'tolerance': tolerance,
            'flip': flip,
            'symmetry_table': symmetry_table
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['success']

    def revert_selected_to_base(self, geo, base_geo, selected_vertices, bias):
        cmd = {
            'cmd': 'revert_selected_to_base',
            'geo': geo,
            'base_geo': base_geo,
            'selected_vertices': selected_vertices,
            'bias': bias
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['success']
