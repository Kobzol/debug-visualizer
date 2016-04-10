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


class Variable(object):
    def __init__(self, value, type=None, name=None, address=None):
        self.type = type
        self.value = str(value)
        self.name = str(name)
        self.address = str(address)

    def __repr__(self):
        return "{} {}: {} ({})".format(self.type, self.name, self.value,
                                       self.address)
