# -*- coding: utf-8 -*-
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


import enum
import json
import jsonpickle
import struct
import uuid


class CommandType(enum.Enum):
    Loopback = 1
    Execute = 2
    Result = 3
    StopServer = 4


class EnumEncoder(json.JSONEncoder):
    @staticmethod
    def parse_enum(d):
        if "__enum__" in d:
            name, member = d["__enum__"].split(".")
            return getattr(globals()[name], member)
        else:
            return d

    @staticmethod
    def byteify(input):
        if isinstance(input, dict):
            return {EnumEncoder.byteify(key): EnumEncoder.byteify(value)
                    for key, value
                    in input.iteritems()}
        elif isinstance(input, list):
            return [EnumEncoder.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


class Command(object):
    @staticmethod
    def receive(client):
        length = struct.unpack_from("<I", client.recv(4))[0]

        if length < 1:
            raise IOError()

        data = client.recv(length).decode(encoding="utf_8")
        payload = jsonpickle.decode(data)

        return Command(payload["type"], payload["data"], payload["id"])

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())

    def __init__(self, type, data=None, id=None):
        if data is None:
            data = {}

        self.type = type
        self.data = data
        self.id = id if id else Command.generate_id()

    def send(self, socket):
        serialized_data = self.get_serialized_data()
        length = len(serialized_data)
        socket.sendall(struct.pack("<I", length))
        socket.sendall(serialized_data)

    def get_serialized_data(self):
        payload = {
            "data": self.data,
            "type": self.type,
            "id": self.id
        }
        return jsonpickle.encode(payload).encode(encoding="utf_8")

    def send_result(self, socket, result):
        result = Command(CommandType.Result, {"result": result,
                                              "query_id": self.id})
        result.send(socket)

    def send_result_error(self, socket, error):
        result = Command(CommandType.Result, {"error": error,
                                              "query_id": self.id})
        result.send(socket)

    def __repr__(self, *args, **kwargs):
        return "{}, {}, {}".format(str(CommandType(self.type)), self.id,
                                   self.data)
