# -*- coding: utf-8 -*-

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
            TypeCategory.Pointer: self.create_pointer,
            TypeCategory.Reference: self.create_pointer,
            TypeCategory.Struct: self.create_struct,
            TypeCategory.Class: self.create_struct,
            TypeCategory.Array: self.create_vector,
            TypeCategory.Vector: self.create_vector,
            TypeCategory.CString: self.create_basic,
            TypeCategory.Enumeration: self.create_basic
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
