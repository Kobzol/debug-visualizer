# -*- coding: utf-8 -*-

import os

from debugger.debugger_api import StartupInfo
from tests.conftest import setup_debugger

TEST_FILE = "test_startup_info"
TEST_LINE = 15


def test_startup_info(debugger):
    """
    @type debugger: debugger.debugger_api.Debugger
    """
    env_value = "test test_env"
    startup_info = StartupInfo("test1 test2", os.getcwd(),
                               [("DEVI_ENV_TEST", env_value)])

    def test_startup_info_cb():
        lines = []

        for x in xrange(5):
            lines.append(debugger.io_manager.stdout.readline()[:-1])

        assert lines == [
            "3",
            os.path.abspath("src/{}".format(TEST_FILE)),
            "test1",
            "test2",
            env_value
        ]

    setup_debugger(debugger, TEST_FILE, TEST_LINE,
                   test_startup_info_cb, startup_info)
