# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import re


class LldbHelper(object):
    def parse_var_description(self, data):
        match = re.search(r"([^=]*)=(.*)", data)
        return (match.group(1).strip(), match.group(2).strip())

    def parse_var_descriptions(self, data):
        variables = []

        for line in data.split("\n"):
            if "=" in line:
                variables.append(self.parse_var_description(line))

        return variables

    def _get_variables_info(self, var_descriptions):
        """
        Returns the given variable names as a list of gdb.Values.

        var_descriptions: list of tuples in the form (name, value) of
        visible variables
        """
        vars = []

        """for var in var_descriptions:
            gdb_val = gdb.parse_and_eval(var[0])
            basic_var = Variable(str(gdb_val),
            Type.from_gdb_type(gdb_val.type), var[0], gdb_val.address)
            vars.append(basic_var)"""

        return vars

    def get_variables(self, name):
        """descriptions = self.parse_var_descriptions(gdb.execute("info " +
        str(name), to_string=True))
        return self._get_variables_info(descriptions)"""
        return None

    def get_locals(self):
        return self.get_variables("locals")

    def get_args(self):
        return self.get_variables("args")

    def get_globals(self):
        return self.get_variables("variables")
