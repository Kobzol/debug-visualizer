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

# -*- coding: utf-8 -*-

import os

DIR_GUI = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.dirname(DIR_GUI)

DIR_DEBUGGER = os.path.join(DIR_ROOT, "debugger")
DIR_RES = os.path.join(DIR_ROOT, "res")


def get_root_path(path):
    return os.path.join(DIR_ROOT, path)


def get_resource(path):
    return os.path.join(DIR_RES, path)
