# -*- coding: utf-8 -*-

class Variable(object):
    def __init__(self, value, type=None, name=None):
        self.type = type
        self.value = value
        self.name = name
        
    def __repr__(self):
        return str(self.type) + " " + str(self.name) + ": " + str(self.value)