import os

import pytest
import time

import sys

from mi.debugger import Debugger
from mi.parser import Parser

TEST_DIR = os.path.dirname(__file__)
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "debugger")

sys.path.append(SRC_DIR)


@pytest.fixture(scope="function")
def debugger():
    return Debugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()


def wait_until_state(debugger, state):
    """
    @type state: enums.ProcessState
    """
    while debugger.get_process_state() != state:
        time.sleep(0.1)
