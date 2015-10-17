# -*- coding: utf-8 -*-

import drawable
from enums import TypeCategory


class MemToViewTransformer(object):
    def __init__(self):
        self.basic_drawable_map = {
            TypeCategory.Builtin: drawable.SimpleVarDrawable,
            TypeCategory.Pointer: drawable.PointerDrawable,
            TypeCategory.Struct: drawable.StructDrawable,
            TypeCategory.Vector: drawable.VectorDrawable
        }

        self.custom_drawable_map = {
            "std::string": drawable.StringDrawable
        }

    def find_drawable(self, type):
        if type.type_category == TypeCategory.Invalid:
            return None

        type_name = type.name

        if type_name in self.custom_drawable_map:
            return self.custom_drawable_map[type_name]
        elif type.type_category in self.basic_drawable_map:
            return self.basic_drawable_map[type.type_category]
        else:
            return None

    def transform_var(self, var):
        drawable_class = self.find_drawable(var.type)

        if drawable_class is not None:
            return drawable_class(var)
        else:
            return None

    def transform_frame(self, vars):
        frame = drawable.StackFrameDrawable()

        for var in vars:
            transformed = self.transform_var(var)

            if transformed is not None:
                frame.add_variable(transformed)

        return frame
