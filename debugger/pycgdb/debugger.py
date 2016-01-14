import os
from elftools.elf.elffile import ELFFile

from debuginfo import DebugInfo


class Debugger(object):
    def __init__(self):
        self.loaded_file = None
        self.debug_info = None

    def load_binary(self, file):
        file = os.path.abspath(file)

        assert os.path.isfile(file)

        with open(file, "r") as binary_file:
            elffile = ELFFile(binary_file)
            assert elffile.has_dwarf_info()

            self.loaded_file = file
            self.debug_info = DebugInfo(elffile)
