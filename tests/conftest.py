# -*- coding: utf-8 -*-

import os
import pytest
import sys

import src.compile as compile

path = os.path.dirname(__file__)

TEST_DIR = os.path.dirname(__file__)
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)
os.chdir(TEST_DIR)

from mi.mi_debugger import MiDebugger  # noqa
from mi.parser import Parser  # noqa


compile.compile_tests()


@pytest.fixture(scope="function")
def debugger():
    return MiDebugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()
