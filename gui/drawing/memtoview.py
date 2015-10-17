# -*- coding: utf-8 -*-

import drawable
from lldbc.lldb_enums import ClassType


class MemToViewTransformer(object):
    def __init__(self):
        self.basic_drawable_map = {
            ClassType.Builtin: drawable.SimpleVarDrawable,
            ClassType.Pointer: drawable.PointerDrawable,
            ClassType.Struct: drawable.StructDrawable,
            ClassType.Vector: drawable.VectorDrawable
        }

        self.custom_drawable_map = {
            "std::string": drawable.StringDrawable
        }

        self.type_replacements = {
            "std::basic_string<char, std::char_traits<char>, std::allocator<char> >": "std::string"
        }

    def unmangle_type_name(self, type):
        type_name = type.name

        clang_inline = "::__1"
        type_name = type_name.replace(clang_inline, "")

        if type_name in self.type_replacements:
            type_name = self.type_replacements[type_name]

        return type_name  # TODO: strip typedefs

    def find_drawable(self, type):
        type_class = ClassType(type.type)

        if type_class == ClassType.Invalid:
            return None

        type_name = self.unmangle_type_name(type)

        if type_name in self.custom_drawable_map:
            return self.custom_drawable_map[type_name]
        elif type_class in self.basic_drawable_map:
            return self.basic_drawable_map[type_class]
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