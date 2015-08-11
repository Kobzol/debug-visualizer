# -*- coding: utf-8 -*-

from enum import IntEnum
import json
from sys import byteorder

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
                
        data = json.loads(client.recv(length).decode(encoding="utf_8"))
        return DebugCommand(data["type"], data)
    
    def __init__(self, type, data):
        self.type = type
        self.data = data
        self.data["type"] = type
    
    def send(self, socket):
        serialized_data = self.get_serialized_data()
        length = len(serialized_data)
        socket.sendall(length.to_bytes(4, byteorder = "little"))
        socket.sendall(serialized_data)
        
    def get_serialized_data(self):
        return json.dumps(self.data).encode(encoding="utf_8")