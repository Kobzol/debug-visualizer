# -*- coding: utf-8 -*-

import os
import pytest
import sys

from tests.src import compile

path = os.path.dirname(os.path.abspath(__file__))

TEST_DIR = path
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)
os.chdir(TEST_DIR)

from debugger.mi.mi_debugger import MiDebugger  # noqa
from debugger.mi.parser import Parser  # noqa


compile.compile_tests()


@pytest.fixture(scope="function")
def debugger():
    return MiDebugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()
