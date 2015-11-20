# -*- coding: utf-8 -*-

import json
import re


class MiParser(object):
    def __init__(self):
        pass

    def parse_breakpoint(self, data):
        return self._parse(data)["bkpt"]

    def parse_breakpoints(self, data):
        pass

    def _prep_json(self, data):
        data = re.sub("((?:\w|-)+)=", r'"\1":', data)
        data = "{" + data + "}"

        return data

    def _parse_json(self, data):
        return json.loads(data)

    def _parse(self, data):
        return self._parse_json(self._prep_json(data))