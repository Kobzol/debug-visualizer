# -*- coding: utf-8 -*-

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
