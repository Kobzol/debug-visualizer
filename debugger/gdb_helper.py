# -*- coding: utf-8 -*-

import gdb
import re
from variable import Variable

class GdbHelper(object):
    def extract_variable(self, data):
        match = re.search(r"([^=]*)=(.*)", data)
        return Variable(name=match.group(1).strip(), value=match.group(2).strip())
    
    def extract_variables(self, data):
        variables = []
        
        for line in data.split("\n"):
            if "=" in line:
                variables.append(self.extract_variable(line))
            
        return variables
    
    def get_locals(self):
        return self.extract_variables(gdb.execute("info locals", to_string=True))
    
    def get_args(self):
        return self.extract_variables(gdb.execute("info args", to_string=True))