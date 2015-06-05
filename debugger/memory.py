# -*- coding: utf-8 -*-

import type

class MemoryBlock(object):
    def __init__(self, address, length, type=None):
        self.address = str(address)
        self.length = int(length)
        self.type = type
        
    def __repr__(self):
        return str(self.address) + " (" + str(self.length) + ", " + str(self.type) + ")"
    
class Memory(object):
    def __init__(self):
        self.blocks = []
        
    def match_pointers(self, variables):
        pointers = []
        for var in variables:
            if var.type.code == type.TypeCode.Pointer:
                pointers.append(var)
                
        for pointer in pointers:
            for block in self.blocks:
                if block.address == pointer.value:
                    block.type = pointer.type.target
    
    def malloc(self, address, length):
        if address and len(address) > 0:
            self.blocks.append(MemoryBlock(address, length))
            
    def free(self, address):
        freed_block = [ block for block in self.blocks if block.address == address ]
        
        if len(freed_block) == 0:
            print("DOUBLE FREE!")
        else:
            self.blocks[:] = [ block for block in self.blocks if block.address != address ]