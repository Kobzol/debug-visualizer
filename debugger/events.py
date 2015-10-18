# -*- coding: utf-8 -*-


class EventBroadcaster(object):
    def __init__(self):
        self.listeners = []

    def notify(self, *args):
        map(lambda listener: listener(*args), self.listeners)

    def subscribe(self, listener):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def clear(self):
        self.listeners = []

    def redirect(self, broadcaster):
        self.subscribe(broadcaster.notify)
