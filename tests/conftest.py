import os

import pytest
import time

import sys

TEST_DIR = os.path.dirname(__file__)
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)
os.chdir(TEST_DIR)

from mi.debugger import Debugger
from mi.parser import Parser


@pytest.fixture(scope="function")
def debugger():
    return Debugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()
