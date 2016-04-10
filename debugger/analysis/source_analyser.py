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

import glob


clang_path = glob.glob("/usr/lib/*/*/libclang.so*")

if len(clang_path) < 1:
    clang_path = glob.glob("/usr/lib/libclang.so")

if len(clang_path) < 1:
    raise BaseException("Clang was not found")

import clang.cindex as cindex  # noqa

cindex.Config.set_library_file(clang_path[0])


class SourceAnalyzer(object):
    def __init__(self, file_path=None):
        self.tu = None
        self.file = None

        if file_path:
            self.set_file(file_path)

    def _create_tu_from_file(self, file_path):
        return cindex.TranslationUnit.from_source(file_path, [])

    def _get_location(self, offset, column=None):
        if column:
            return cindex.SourceLocation.from_position(self.tu, self.file,
                                                       offset,
                                                       column)
        else:
            return cindex.SourceLocation.from_offset(self.tu, self.file,
                                                     offset)

    def set_file(self, file_path):
        """
        Parses the given file and returns whether the parsing was successful.
        @type file_path: str
        @rtype: bool
        """
        try:
            self.tu = self._create_tu_from_file(file_path)
            self.file = cindex.File.from_name(self.tu, file_path)
            return True
        except:
            return False

    def get_symbol_name(self, line, column=None):
        """
        Get's name of a symbol defined on the given line and column.
        Returns None if no symbol was found or if no file is loaded.
        @type line: int
        @type column: int
        @rtype: str | None
        """
        if self.tu is None or self.file is None:
            return None

        location = self._get_location(line, column)
        cursor = cindex.Cursor.from_location(self.tu, location)

        return cursor.spelling
