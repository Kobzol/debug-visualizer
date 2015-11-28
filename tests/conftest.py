import os
import sys

import pytest

import src.compile as compile

path = os.path.dirname(__file__)

TEST_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)
os.chdir(TEST_DIR)

from mi.debugger import Debugger
from mi.parser import Parser


compile.compile_tests()


@pytest.fixture(scope="function")
def debugger():
    return Debugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()
