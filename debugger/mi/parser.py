# -*- coding: utf-8 -*-

import json
import re

from breakpoint import Breakpoint
from enums import ThreadState
from frame import Frame
from inferior_thread import InferiorThread, ThreadInfo


class Parser(object):
    def __init__(self):
        pass

    def parse_breakpoint(self, data):
        return self._instantiate_breakpoint(self.parse(data)["bkpt"])

    def parse_breakpoints(self, data):
        return [self._instantiate_breakpoint(bp) for bp in self.parse(data)["BreakpointTable"]["body"]]

    def parse_thread_info(self, data):
        """
        @type data: str
        @return: inferior_thread.ThreadInfo
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
        @return: list of frame.Frame
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
        @return: str
        """
        return data[7:]

    def parse_disassembly(self, data):
        lines_dis = self.parse(data)["asm_insns"]
        lines = []
        for line in lines_dis:
            line_data = line["line_asm_insn"]
            line_obj = {
                "line" : line["line"],
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
        @return: dict
        """
        return self.parse(data)

    def parse_frame_variables(self, data):
        """
        @type data: str
        @return: dict
        """
        return self.parse(data)["variables"]

    def parse_struct_member_names(self, data):
        """
        @type data: str
        @return: list of str
        """
        data = data.replace("'", "\"")
        return self._parse_json(data)

    def parse(self, data):
        return self._parse_json(self._prep_json(data))

    def _instantiate_thread(self, thread):
        return InferiorThread(int(thread["id"]), thread["name"], self._instantiate_thread_state(thread["state"]), self._instantiate_frame(thread["frame"]))

    def _instantiate_frame(self, frame):
        """
        @type frame: dict
        @return: frame.Frame
        """
        level = int(frame.get("level", "0"))
        func = frame.get("func", "")
        fullname = frame.get("fullname", "")
        line = int(frame.get("line", "0"))

        return Frame(level, func, fullname, line)

    def _instantiate_thread_state(self, state):
        """
        @type state: str
        @return: enums.ThreadState | None
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
        return Breakpoint(int(bp["number"]), bp["fullname"], int(bp["line"]))

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
                    while j < len(data) and (data[j].isalpha() or data[j] == "_" or data[j] == "="):
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

    def _prep_json(self, data):
        # remove array labels
        data = self._remove_array_labels(data)
        data = re.sub("((?:\w|-)+)\s*=", r'"\1":', data)
        data = re.sub("<error reading variable[^>]*>", "\"\"", data)

        if data[0] not in ("{", "["):
            data = "{" + data + "}"

        return data

    def _parse_json(self, data):
        return json.loads(data)
