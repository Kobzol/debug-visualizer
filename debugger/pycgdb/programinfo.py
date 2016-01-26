import os


class ProgramInfo(object):
    def __init__(self, elffile):
        """
        @type elffile: elftools.elf.elffile.ELFFile
        """

        dwarf_info = elffile.get_dwarf_info()
        self.files = {}
        self.addresses = {}

        for cu in dwarf_info.iter_CUs():
            line_program = dwarf_info.line_program_for_CU(cu)

            if line_program:
                for line_entry in line_program.get_entries():
                    if line_entry.state:
                        self._parse_line_state(line_program.header.file_entry, line_entry.state)

            for die in cu.iter_DIEs():
                self._parse_die(die)

    def has_file(self, file):
        return os.path.abspath(file) in self.files

    def has_location(self, file, line):
        file = os.path.abspath(file)

        return self.has_file(file) and line in self.files[file]

    def get_address(self, file, line):
        file = os.path.abspath(file)

        if not self.has_location(file, line):
            return None
        else:
            return self.files[file][line][0]

    def get_location(self, address):
        if address in self.addresses:
            return self.addresses[address]
        else:
            return None

    def _parse_die(self, die):
        for child in die.iter_children():
            self._parse_die(child)

    def _parse_line_state(self, files, line_state):
        file = os.path.abspath(files[line_state.file - 1].name)
        line = line_state.line
        address = line_state.address

        if not file in self.files:
            self.files[file] = {}

        if not line in self.files[file]:
            self.files[file][line] = []

        self.files[file][line].append(address)
        self.addresses[address] = (file, line)
