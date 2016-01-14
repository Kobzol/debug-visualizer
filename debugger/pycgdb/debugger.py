import os
from elftools.elf.elffile import ELFFile

from programinfo import ProgramInfo
from pycgdb.breakpoint_manager import BreakpointManager
from pycgdb.programrunner import ProgramRunner


class Debugger(object):
    def __init__(self):
        self.loaded_file = None
        self.program_info = None
        self.runner = None
        self.breakpoint_manager = BreakpointManager(self)

    def load_binary(self, file):
        file = os.path.abspath(file)

        assert os.path.isfile(file)

        with open(file, "r") as binary_file:
            elffile = ELFFile(binary_file)
            assert elffile.has_dwarf_info()

            self.loaded_file = file
            self.program_info = ProgramInfo(elffile)
