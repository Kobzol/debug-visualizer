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


import drawable
from debugger.enums import TypeCategory
from geometry import Padding
from size import Size


class MemToViewTransformer(object):
    def __init__(self, canvas):
        """
        @type canvas: canvas.Canvas
        """
        self.function_map = {
            TypeCategory.Builtin: self.create_basic,
            TypeCategory.String: self.create_basic,
            TypeCategory.CString: self.create_basic,
            TypeCategory.Enumeration: self.create_basic,
            TypeCategory.Function: self.create_basic,
            TypeCategory.Pointer: self.create_pointer,
            TypeCategory.Reference: self.create_pointer,
            TypeCategory.Struct: self.create_struct,
            TypeCategory.Class: self.create_struct,
            TypeCategory.Union: self.create_struct,
            TypeCategory.Array: self.create_vector,
            TypeCategory.Vector: self.create_vector
        }
        self.canvas = canvas

    def create_struct(self, var):
        """
        @type var: debugee.Variable
        @rtype: drawable.StructDrawable
        """
        return drawable.StructDrawable(self.canvas, var)

    def create_pointer(self, var):
        """
        @type var: debugee.Variable
        @rtype: drawable.PointerDrawable
        """
        return drawable.PointerDrawable(self.canvas, var,
                                        padding=Padding.all(5),
                                        size=Size(-1, 20))

    def create_basic(self, var):
        """
        @type var: debugee.Variable
        @rtype: drawable.VariableDrawable
        """
        return drawable.VariableDrawable(self.canvas, var,
                                         padding=Padding.all(5),
                                         size=Size(-1, 20),
                                         max_size=Size(150, -1))

    def create_vector(self, var):
        """
        @type var: debugee.Variable
        @rtype: drawable.VectorDrawable
        """
        return drawable.VectorDrawable(self.canvas, var)

    def transform_var(self, var):
        """
        @type var: debugee.Variable
        @rtype drawable.Drawable
        """
        type = var.type

        if not type.is_valid():
            return None

        create_fn = self.function_map.get(type.type_category, None)

        if create_fn:
            return create_fn(var)
        else:
            return None

    def transform_frame(self, frame):
        """
        @type frame: debugee.Frame
        @rtype: drawable.StackFrameDrawable
        """
        frame_drawable = drawable.StackFrameDrawable(self.canvas, frame)
        return frame_drawable
