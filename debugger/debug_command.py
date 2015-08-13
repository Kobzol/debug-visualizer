# -*- coding: utf-8 -*-

from enum import IntEnum
import json
from sys import byteorder
import uuid

class CommandType(IntEnum):
    LoopbackCommand = 1,
    ExecuteCommand = 2,
    ResultCommand = 3

class DebugCommand(object):
    @staticmethod
    def receive(client):
        length = int.from_bytes(client.recv(4), byteorder = "little")
                
        if length < 1:
            raise IOError()
                
        payload = json.loads(client.recv(length).decode(encoding="utf_8"))
        
        return DebugCommand(payload["type"], payload["data"], payload["id"])
    
    def __init__(self, type, data, id = None):
        self.type = type
        self.data = data
        self.id = id if id else self.generate_id()
    
    def generate_id(self):
        return str(uuid.uuid4())
    
    def send(self, socket):
        serialized_data = self.get_serialized_data()
        length = len(serialized_data)
        socket.sendall(length.to_bytes(4, byteorder = "little"))
        socket.sendall(serialized_data)
        
    def get_serialized_data(self):
        payload = {
            "data" : self.data,
            "type" : self.type,
            "id" : self.id
        }
        return json.dumps(payload).encode(encoding="utf_8")
    
    def send_result(self, socket, result):
        result = DebugCommand(CommandType.ResultCommand, {"result" : result, "query_id" : self.id})
        result.send(socket)