# -*- coding: utf-8 -*-
from enums import DebuggerState


class LldbVariableEditor(object):
    def __init__(self, debugger):
        """
        @type debugger: lldbc.lldb_debugger.LldbDebugger
        """
        self.debugger = debugger

    def change_variable_in_frame(self, frame, variable):
        """
        @type frame: lldb.SBFrame
        @type variable: variable.Variable
        """
        self.debugger.require_state(DebuggerState.Running)
        frame.EvaluateExpression(variable.path + " = " + variable.value)
