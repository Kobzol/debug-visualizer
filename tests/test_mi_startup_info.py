# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import time
import pytest

from debugger.debugger_api import StartupInfo
from debugger.enums import ProcessState, DebuggerState

STARTUP_FILE = "src/test_startup_info.cpp"
STARTUP_EXECUTABLE_FILE = "src/test_startup_info"
LINE = 15


def prepare_debugger(debugger, startup_info, on_state_change=None):
    debugger.load_binary(STARTUP_EXECUTABLE_FILE)
    debugger.breakpoint_manager.add_breakpoint(STARTUP_FILE, LINE)

    if on_state_change:
        def on_stop(state, data):
            if state == ProcessState.Stopped:
                try:
                    on_state_change()
                except Exception as exc:
                    pytest.fail(exc, pytrace=True)
                finally:
                    debugger.quit_program()

        debugger.on_process_state_changed.subscribe(on_stop)

    debugger.launch(startup_info)

    while debugger.state.is_set(DebuggerState.Running):
        time.sleep(0.1)


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
            os.path.abspath(STARTUP_EXECUTABLE_FILE),
            "test1",
            "test2",
            env_value
        ]

    prepare_debugger(debugger, startup_info, test_startup_info_cb)
