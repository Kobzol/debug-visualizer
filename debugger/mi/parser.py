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

import json
import re

from debugger.debugee import Breakpoint, InferiorThread, ThreadInfo, Frame
from debugger.enums import ThreadState


class Parser(object):
    def __init__(self):
        pass

    def parse_breakpoint(self, data):
        return self._instantiate_breakpoint(self.parse(data)["bkpt"])

    def parse_breakpoints(self, data):
        return [self._instantiate_breakpoint(bp)
                for bp
                in self.parse(data)["BreakpointTable"]["body"]]

    def parse_thread_info(self, data):
        """
        @type data: str
        @rtype: debugee.ThreadInfo
        """
        data = self.parse(data)
        current_thread_id = int(data["current-thread-id"])
        current_thread = None
        threads = []

        for thread in data["threads"]:
            th = self._instantiate_thread(thread)
            threads.append(th)

            if th.id == current_thread_id:
                current_thread = th

        return ThreadInfo(current_thread, threads)

    def parse_stack_frames(self, data):
        """
        @type data: str
        @rtype: list of debugee.Frame
        """
        data = self.parse(data)["stack"]
        frames = []

        for frame in data:
            frames.append(self._instantiate_frame(frame))

        return frames

    def parse_stack_frame(self, data):
        return self._instantiate_frame(self.parse(data)["frame"])

    def parse_variable_type(self, data):
        """
        @type data: str
        @rtype: str
        """
        return data[7:]

    def parse_disassembly(self, data):
        lines_dis = self.parse(data)["asm_insns"]
        lines = []
        for line in lines_dis:
            line_data = line["line_asm_insn"]
            line_obj = {
                "line": int(line["line"]),
                "instructions": []
            }
            for inst in line_data:
                line_obj["instructions"].append(inst["inst"])

            lines.append(line_obj)

        return lines

    def parse_print_expression(self, data):
        data = "".join(data)
        data = data[data.find("=") + 2:].replace("\\\"", "\"")

        return data

    def parse_struct(self, data):
        """
        @type data: str
        @rtype: dict
        """
        return self.parse(data)

    def parse_frame_variables(self, data):
        """
        @type data: str
        @rtype: dict
        """
        return self.parse(data)["variables"]

    def parse_struct_member_names(self, data):
        """
        @type data: str
        @rtype: list of str
        """
        data = data.replace("'", "\"")
        return self._parse_json(data)

    def parse(self, data):
        return self._parse_json(self._prep_json(data))

    def _instantiate_thread(self, thread):
        return InferiorThread(int(thread["id"]), thread["name"],
                              self._instantiate_thread_state(thread["state"]),
                              self._instantiate_frame(thread["frame"]))

    def _instantiate_frame(self, frame):
        """
        @type frame: dict
        @rtype: debugee.Frame
        """
        level = int(frame.get("level", "0"))
        func = frame.get("func", "")
        fullname = frame.get("fullname", "")
        line = int(frame.get("line", "0"))

        return Frame(level, func, fullname, line)

    def _instantiate_thread_state(self, state):
        """
        @type state: str
        @rtype: enums.ThreadState | None
        """
        map = {
            "running": ThreadState.Running,
            "stopped": ThreadState.Stopped,
            "exited": ThreadState.Exited
        }

        if state in map:
            return map[state]
        else:
            return None

    def _instantiate_breakpoint(self, bp):
        if "fullname" not in bp:
            name = ""
        else:
            name = bp["fullname"]
        return Breakpoint(int(bp["number"]), name, int(bp["line"]))

    def _remove_array_labels(self, data):
        in_array = []

        i = 0
        in_quote = False

        while i < len(data):
            char = data[i]

            if char == "\"":
                in_quote = not in_quote

            if not in_quote:
                if char == "[":
                    in_array.append(1)
                if char == "{":
                    in_array.append(0)
                if char in ("]", "}"):
                    in_array.pop()

                if len(in_array) > 0 and in_array[-1] == 1:
                    j = i
                    while (j < len(data) and
                           (data[j].isalpha() or
                            data[j] == "_" or
                            data[j] == "=")):
                        j += 1

                    if j > i:
                        data = data[:i] + data[j:]
                        i -= 1
            i += 1

        for parentheses in in_array:
            if parentheses == 1:
                data += "]"
            elif parentheses == 0:
                data += "}"

        return data

    def _modify_labels(self, data):
        """
        Changes keys in the form ([a-zA-Z-_])+\s*= to "\1":
        (replaces = with :, removes whitespace and adds quotes).
        @type data: str
        @rtype: str
        """
        in_str = False
        in_ident = False
        start_ident = 0
        i = 0

        while i < len(data):
            char = data[i]

            if char == "\"":
                in_str = not in_str

            if in_str:
                i += 1
                continue

            matches_ident = re.match("[a-zA-Z-_]", char) is not None
            if not in_ident and matches_ident:
                in_ident = True
                start_ident = i

            if in_ident and re.match("\s", char) is not None:
                i += 1
                continue

            if in_ident and char == "=":
                old_length = len(data)
                data = data[:start_ident] + re.sub("^((?:[a-zA-Z-_])+)\s*=",
                                                   r'"\1":',
                                                   data[start_ident:])
                diff = old_length - len(data)
                i -= diff

                in_ident = False
            elif in_ident and not matches_ident:
                raise BaseException("Wrong attribute key")

            i += 1

        return data

    def _prep_json(self, data):
        if len(data) < 1:
            return data

        # remove array labels
        data = self._remove_array_labels(data)
        data = self._modify_labels(data)
        data = re.sub("<error reading variable[^>]*>", "\"\"", data)

        if data[0] not in ("{", "["):
            data = "{" + data + "}"

        return data

    def _parse_json(self, data):
        if len(data) < 1:
            return data
        else:
            return json.loads(data)
