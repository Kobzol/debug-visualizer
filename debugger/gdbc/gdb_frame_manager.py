# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015-2016 Jakub Beranek
#
#    This file is part of Devi.
#
#    Devi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Devi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Devi.  If not, see <http://www.gnu.org/licenses/>.
#


import gdb


class GdbFrameManager(object):
    def get_frames(self):
        frame_lines = gdb.execute("bt", to_string=True)
        frames = []
        frame = ""

        for line in frame_lines.split("\n"):
            if len(line) > 0 and line[0] == "#":
                if frame != "":
                    frames.append(frame.strip())
                frame = line
            else:
                frame += " " + line

        frames.append(frame.strip())

        return frames
