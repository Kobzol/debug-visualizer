# -*- coding: utf-8 -*-

import gdb


class GdbFileManager(object):
    """
    Returns tuple (filename, line_number).
    """
    def get_current_location(self):
        try:
            frame = gdb.selected_frame()
            sal = frame.find_sal()
            symtab = sal.symtab

            return (symtab.fullname(), sal.line)
        except:
            return None
