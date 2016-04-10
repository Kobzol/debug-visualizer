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

import os
from elftools.elf.elffile import ELFFile

from programinfo import ProgramInfo
from breakpoint_manager import BreakpointManager
from programrunner import ProgramRunner


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
            self.runner = ProgramRunner(self, file)

    def run(self, *args):
        self.runner.args = args
        self.runner.run()
