# -*- coding: utf-8 -*-

import drawable
from enums import TypeCategory


class MemToViewTransformer(object):
    def __init__(self):
        self.function_map = {
            TypeCategory.Builtin: self.create_basic,
            TypeCategory.String: self.create_basic,
            TypeCategory.Pointer: self.create_pointer,
            TypeCategory.Reference: self.create_pointer,
            TypeCategory.Struct: self.create_struct,
            TypeCategory.Class: self.create_struct,
            TypeCategory.Array: self.create_vector,
            TypeCategory.Vector: self.create_vector
        }

    def create_struct(self, canvas, var):
        """
        @type var: variable.Variable
        @rtype: drawable.Drawable
        """
        container = drawable.StructDrawable(canvas, var)

        for child in var.children:
            var = self.transform_var(canvas, child)

            if var:
                container.add_child(var)

        return container

    def create_pointer(self, canvas, var):
        return drawable.VariableDrawable(canvas, var)

    def create_basic(self, canvas, var):
        return drawable.VariableDrawable(canvas, var)

    def create_vector(self, canvas, var):
        return drawable.VectorDrawable(canvas, var)

    def transform_var(self, canvas, var):
        """
        @type var: variable.Variable
        @rtype drawable.Drawable
        """
        type = var.type

        if not type.is_valid():
            return None

        create_fn = self.function_map.get(type.type_category, None)

        if create_fn:
            return create_fn(canvas, var)
        else:
            return None

    def transform_frame(self, canvas, frame):
        """
        @type canvas: canvas.Canvas
        @type frame: frame.Frame
        @rtype: drawable.StackFrameDrawable
        """
        frame_drawable = drawable.StackFrameDrawable(canvas, frame)

        for var in frame.variables:
            transformed = self.transform_var(canvas, var)

            if transformed is not None:
                frame_drawable.add_child(transformed)

        return frame_drawable
