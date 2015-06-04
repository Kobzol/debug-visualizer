# -*- coding: utf-8 -*-

class MemoryBlock(object):
    def __init__(self, address, length, type=None):
        self.address = address
        self.length = length
        self.type = type
        
    def __repr__(self):
        return str(self.address) + " (" + str(self.length) + ", " + str(self.type) + ")"