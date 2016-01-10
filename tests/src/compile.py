import os
import subprocess

src_path = os.path.dirname(os.path.abspath(__file__))


def compile_tests():
    for file in os.listdir(src_path):
        if file.endswith(".cpp"):
            subprocess.check_call(["g++", "-g", "-O0", "-pthread", "-std=c++11", "{}".format(os.path.join(src_path, file)),
                                   "-o{}".format(os.path.join(src_path, os.path.splitext(file)[0]))])


if __name__ == "__main__":
    compile_tests()
