# -*- coding: utf-8 -*-

class MemoryBlock(object):
    def __init__(self, address, length, type=None):
        self.address = address
        self.length = length
        self.type = type
        
    def __repr__(self):
        return str(self.address) + " (" + str(self.length) + ", " + str(self.type) + ")"
    
class Memory(object):
    def __init__(self):
        self.blocks = []
    
    def malloc(self, address, length):
        if address and len(address) > 0:
            self.blocks.append(MemoryBlock(address, address))
            
    def free(self, address):
        freed_block = [ block for block in self.blocks if block.address == address ]
        
        if len(freed_block) == 0:
            print("DOUBLE FREE!")
        else:
            self.blocks[:] = [ block for block in self.blocks if block.address != address ]