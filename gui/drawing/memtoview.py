# -*- coding: utf-8 -*-

from drawable import StackFrameDrawable, SimpleVarDrawable


class MemToViewTransformer(object):
    def __init__(self):
        self.memtoviewmap = {
            "int": SimpleVarDrawable,
            "float": SimpleVarDrawable,
            "double": SimpleVarDrawable,
            "bool": SimpleVarDrawable
        }

    def unmangle_type_name(self, type_name):
        return type_name  # TODO: unmangle libc++ namespaced names

    def transform_var(self, var):
        type_name = self.unmangle_type_name(var.type.name)

        if type_name not in self.memtoviewmap:
            return None

        drawable_class = self.memtoviewmap[type_name]
        return drawable_class(var)

    def transform_frame(self, vars):
        frame = StackFrameDrawable()

        for var in vars:
            transformed = self.transform_var(var)

            if transformed is not None:
                frame.add_variable(transformed)

        return frame