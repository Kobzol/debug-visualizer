# -*- coding: utf-8 -*-

import gdb
import re
import subprocess
from variable import Variable
from type import Type

class GdbHelper(object):
    def parse_var_description(self, data):
        match = re.search(r"([^=]*)=(.*)", data)
        return (match.group(1).strip(), match.group(2).strip())
    
    def parse_var_descriptions(self, data):
        variables = []
        
        for line in data.split("\n"):
            if "=" in line:
                variables.append(self.parse_var_description(line))
            
        return variables
    
    def _get_variables_info(self, var_descriptions):
        """
        Returns the given variable names as a list of gdb.Values.
        
        var_descriptions: list of tuples in the form (name, value) of visible variables
        """
        vars = []
        
        for var in var_descriptions:
            gdb_val = gdb.parse_and_eval(var[0])
            basic_var = Variable(str(gdb_val), Type.from_gdb_type(gdb_val.type), var[0], gdb_val.address)
            vars.append(basic_var)
            
        return vars
    
    def get_variables(self, name):
        descriptions = self.parse_var_descriptions(gdb.execute("info " + str(name), to_string=True))
        return self._get_variables_info(descriptions)
    
    def get_locals(self):
        return self.get_variables("locals")
    
    def get_args(self):
        return self.get_variables("args")
        
    def get_globals(self):
        return self.get_variables("variables")