# -*- coding: utf-8 -*-

from enum import Enum
import json
from sys import byteorder
import uuid
import struct

class CommandType(Enum):
    Loopback = 1
    Execute = 2
    Result = 3

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
            return { EnumEncoder.byteify(key) : EnumEncoder.byteify(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [ EnumEncoder.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)

class Command(object):
    @staticmethod
    def receive(client):
        length = struct.unpack_from("<I", client.recv(4))[0]
                
        if length < 1:
            raise IOError()
                
        data = client.recv(length).decode(encoding="utf_8")
        payload = EnumEncoder.byteify(json.loads(data, object_hook=EnumEncoder.parse_enum))
        
        return Command(payload["type"], payload["data"], payload["id"])
    
    def __init__(self, type, data = {}, id = None):
        self.type = type
        self.data = data
        self.id = id if id else self.generate_id()
    
    def generate_id(self):
        return str(uuid.uuid4())
    
    def send(self, socket):
        serialized_data = self.get_serialized_data()
        length = len(serialized_data)
        socket.sendall(struct.pack("<I", length))
        socket.sendall(serialized_data)
        
    def get_serialized_data(self):
        payload = {
            "data" : self.data,
            "type" : self.type,
            "id" : self.id
        }
        return json.dumps(payload, cls=EnumEncoder).encode(encoding="utf_8")
    
    def send_result(self, socket, result):
        result = Command(CommandType.Result, {"result" : result, "query_id" : self.id})
        result.send(socket)
    
    def send_result_error(self, socket, error):
        result = Command(CommandType.Result, {"error" : error, "query_id" : self.id})
        result.send(socket)
    
    def __repr__(self, *args, **kwargs):
        return str(CommandType(self.type)) + ", " + str(self.id) + ", " + str(self.data)