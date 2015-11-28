# -*- coding: utf-8 -*-
import re
import traceback

from util import Logger


class FileManager(object):
    def __init__(self, debugger):
        """
        @type debugger: mi.debugger.Debugger
        """
        self.debugger = debugger

    def _get_current_line(self):
        output = self.debugger.communicator.send("info line")

        try:
            if output:
                cli_data = output.cli_data[0][5:]
                match = re.match("(\d+)", cli_data)

                return int(match.group(0))
        except Exception as e:
            traceback.print_exc()

        return None

    def _get_current_file(self):
        output = self.debugger.communicator.send("info source")

        try:
            if output:
                cli_data = output.cli_data[2]
                return cli_data[11:]
        except Exception as e:
            traceback.print_exc()

        return None

    def get_main_source_file(self):
        output = self.debugger.communicator.send("info sources")

        if output:
            files = output.cli_data[1]
            return files.split(",")[0]
        else:
            return None

    def get_current_location(self):
        frame = self.debugger.thread_manager.get_current_frame()

        line = frame.line
        location = frame.file

        Logger.debug("Getting current location: ({0}, {1})".format(location, line))

        return (location, line)