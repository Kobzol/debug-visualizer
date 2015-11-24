import os

import subprocess

path = os.path.dirname(__file__)

for file in os.listdir(path):
    if file.endswith(".cpp"):
        subprocess.check_call(["g++", "-g", "-O0", "-std=c++11", "{}".format(file),
                               "-o{}".format(os.path.splitext(file)[0])])
        print("Compiled {0}".format(file))
