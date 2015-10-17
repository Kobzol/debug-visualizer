# -*- coding: utf-8 -*-

class Variable(object):
    def __init__(self, value, type=None, name=None, address=None):
        self.type = type
        self.value = str(value)
        self.name = str(name)
        self.address = str(address)
        
    def __repr__(self):
        return str(self.type) + " " + str(self.name) + ": " + str(self.value) + " (" + str(self.address) + ")"