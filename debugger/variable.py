# -*- coding: utf-8 -*-


class Type(object):
    def __init__(self, name, type_class, basic_class):
        self.name = name
        self.type_class = type_class
        self.basic_class = basic_class


class Variable(object):
    def __init__(self, address=None, name=None, value=None, type=None, path=None):
        self.address = address
        self.name = name
        self.value = value
        self.type = type
        self.path = path

        self.children = []

    def add_child(self, child):
        self.children.append(child)
