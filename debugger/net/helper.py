# -*- coding: utf-8 -*-


class NetHelper(object):
    @staticmethod
    def get_free_port():
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        port = s.getsockname()[1]
        s.close()

        return port