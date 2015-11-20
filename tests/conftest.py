import os

import pytest

from mi.debugger import Debugger
from mi.parser import Parser

TEST_DIR = os.path.dirname(__file__)
TEST_SRC_DIR = os.path.join(TEST_DIR, "src")


@pytest.fixture
def debugger():
    return Debugger()


@pytest.fixture(scope="module")
def parser():
    return Parser()