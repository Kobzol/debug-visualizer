# -*- coding: utf-8 -*-

import json
import re


class MiParser(object):
    def __init__(self):
        pass

    def parse_breakpoint(self, data):
        return self.parse(data)["bkpt"]

    def parse_breakpoints(self, data):
        return self.parse(data)["BreakpointTable"]["body"]

    def parse(self, data):
        return self._parse_json(self._prep_json(data))

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

                if len(in_array) > 0 and in_array[len(in_array) - 1] == 1:
                    j = i
                    while j < len(data) and (data[j].isalpha() or data[j] == "="):
                        j += 1

                    if j > i:
                        changed_str = list(data)
                        changed_str[i:j] = " " * (j - i)
                        data = "".join(changed_str)
                        i += (j - i - 1)

            i += 1

        return data

    def _prep_json(self, data):
        # remove array labels
        data = self._remove_array_labels(data)
        data = re.sub("((?:\w|-)+)=", r'"\1":', data)
        data = "{" + data + "}"

        return data

    def _parse_json(self, data):
        return json.loads(data)
