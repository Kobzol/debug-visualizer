# -*- coding: utf-8 -*-

import drawable
from enums import TypeCategory


class MemToViewTransformer(object):
    def __init__(self):
        self.function_map = {
            TypeCategory.Builtin: self.create_basic,
            TypeCategory.Pointer: self.create_pointer,
            TypeCategory.Struct: self.create_struct,
            TypeCategory.Class: self.create_struct
        }

    def create_struct(self, var):
        """
        @type var: variable.Variable
        @rtype: drawable.Drawable
        """
        container = drawable.StructDrawable(var)

        for child in var.children:
            var = self.transform_var(child)

            if var:
                container.add_child(var)

        return container

    def create_pointer(self, var):
        return drawable.PointerDrawable(var)

    def create_basic(self, var):
        return drawable.SimpleVarDrawable(var)

    def transform_var(self, var):
        """
        @type var: variable.Variable
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

    def transform_frame(self, vars):
        frame = drawable.StackFrameDrawable()

        for var in vars:
            transformed = self.transform_var(var)

            if transformed is not None:
                frame.add_variable(transformed)

        return frame
