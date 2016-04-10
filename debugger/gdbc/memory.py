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

import re

import type


class MemoryBlock(object):
    def __init__(self, address, length, type=None):
        self.address = str(address)
        self.length = int(length)
        self.type = type

    def __repr__(self):
        return "{} ({}, {})".format(self.address, self.length, self.type)


class Memory(object):
    def __init__(self):
        self.blocks = []

    def match_pointers(self, variables):
        pointers = []
        for var in variables:
            if var.type.code == type.TypeCode.Pointer:
                pointers.append(var)

        for pointer in pointers:
            for block in self.blocks:
                if block.address == pointer.value:
                    block.type = pointer.type.target

    def malloc(self, address, length, fn_name):
        if address and len(address) > 0:
            block = MemoryBlock(address, length)

            if fn_name:
                match = re.search(r"operator new\(([^)]*)\)", fn_name)
                if match:
                    type_name = match.group(1)
                    block.type = type_name

            self.blocks.append(block)

    def free(self, address):
        freed_block = [block
                       for block
                       in self.blocks
                       if block.address == address]

        if len(freed_block) == 0:
            print("DOUBLE FREE!")
        else:
            self.blocks[:] = [block
                              for block
                              in self.blocks
                              if block.address != address]
