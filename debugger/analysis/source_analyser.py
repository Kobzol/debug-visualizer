# -*- coding: utf-8 -*-

from clang.cindex import TranslationUnit, File, SourceLocation, Cursor


class SourceAnalyzer(object):
    def __init__(self, file_path=None):
        self.tu = None
        self.file = None

        if file_path:
            self.set_file(file_path)

    def _create_tu_from_file(self, file_path):
        return TranslationUnit.from_source(file_path, [])

    def _get_location(self, offset, column=None):
        if column:
            return SourceLocation.from_position(self.tu, self.file, offset, column)
        else:
            return SourceLocation.from_offset(self.tu, self.file, offset)

    def set_file(self, file_path):
        self.tu = self._create_tu_from_file(file_path)
        self.file = File.from_name(self.tu, file_path)

    def get_symbol_name(self, offset, column=None):
        if self.tu is None or self.file is None:
            return None

        location = self._get_location(offset, column)
        cursor = Cursor.from_location(self.tu, location)

        return cursor.spelling
