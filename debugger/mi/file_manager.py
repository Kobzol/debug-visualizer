# -*- coding: utf-8 -*-

import re
import traceback

import debugger
from mi.parser import Parser
from util import Logger


class FileManager(debugger.FileManager):
    def __init__(self, debugger):
        """
        @type debugger: debugger.Debugger
        """
        super(FileManager, self).__init__(debugger)
        self.parser = Parser()

    def _get_current_line(self):
        output = self.debugger.communicator.send("info line")

        try:
            if output:
                cli_data = output.cli_data[0][5:]
                match = re.match("(\d+)", cli_data)

                return int(match.group(0))
        except:
            traceback.print_exc()

        return None

    def _get_current_file(self):
        output = self.debugger.communicator.send("info source")

        try:
            if output:
                cli_data = output.cli_data[2]
                return cli_data[11:]
        except:
            traceback.print_exc()

        return None

    def _get_single_capture(self, pattern, input):
        match = re.search(pattern, input)
        if not match:
            return None
        else:
            return match.group(1)

    def get_main_source_file(self):
        output = self.debugger.communicator.send("info sources")

        if output:
            files = output.cli_data[1]
            return files.split(",")[0]
        else:
            return None

    def get_current_location(self):
        """
        Returns the current file and line of the debugged process.
        @rtype: tuple of basestring, int | None
        """
        frame = self.debugger.thread_manager.get_current_frame()

        if not frame:
            return None

        line = frame.line
        location = frame.file

        Logger.debug("Getting current location: ({0}, {1})".format(
            location, line))

        return (location, line)

    def get_line_address(self, filename, line):
        """
        Returns the starting address and ending address in hexadecimal format
        of code at the specified line in the given file.
        Returns None if no code is at the given location.
        @type filename: str
        @type line: int
        @rtype: tuple of int | None
        """
        command = "info line {0}:{1}".format(filename, line)
        result = self.debugger.communicator.send(command)

        if result:
            data = result.cli_data[0]
            if "address" not in data or "contains no code" in data:
                return None

            start_address = self._get_single_capture(
                "starts at address ([^ ]*)", data)
            end_address = self._get_single_capture("ends at ([^ ]*)", data)

            if start_address and end_address:
                return (start_address, end_address)
            else:
                return None
        else:
            return None

    def disassemble(self, filename, line):
        """
        Returns disassembled code for the given location.
        Returns None if no code was found,
        @type filename: str
        @type line: int
        @rtype: str | None
        """
        command = "-data-disassemble -f {0} -l {1} -n 10 -- 1".format(filename,
                                                                      line)
        result = self.debugger.communicator.send(command)
        if result:
            disassembled = self.parser.parse_disassembly(result.data)
            if disassembled:
                return disassembled
            else:
                return None
        else:
            return None

    def disassemble_raw(self, filename, line):
        """
        Disassembles the given line in a raw form (returns a string with the
        line and all assembly instructions for it).
        @type filename: str
        @type line: int
        @rtype: str | None
        """
        address = self.get_line_address(filename, line)

        if not address:
            return None

        command = "disas /m {0}, {1}".format(address[0], address[1])
        result = self.debugger.communicator.send(command)
        if result:
            return "\n".join([row.replace("\\t", "\t")
                              for row
                              in result.cli_data[1:-1]])
        else:
            return None
