# -*- coding: utf-8 -*-

import types


class Dispatcher(object):
    @staticmethod
    def dispatch(root_object, properties=None, arguments=None):
        target_prop = root_object

        if properties is None:
            properties = []

        if arguments is not None and not isinstance(arguments, (list, tuple)):
            arguments = [arguments]

        for prop in properties:
            target_prop = getattr(target_prop, prop)

        if hasattr(target_prop, "__call__"):
            if arguments is not None:
                result = target_prop(*arguments)
            else:
                result = target_prop()

            return result
        else:
            return target_prop
