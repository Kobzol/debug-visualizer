# -*- coding: utf-8 -*-


class NetHelper(object):
    """
    Helper class for network operations.
    """
    @staticmethod
    def get_free_port():
        """
        Returns a free port that can be bound.
        @rtype: int
        """
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()

        return port
