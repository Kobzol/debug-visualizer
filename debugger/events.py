# -*- coding: utf-8 -*-


class EventBroadcaster(object):
    """
    Object that broadcasts event to it's listeners.

    Evety broadcaster represents a single event type.
    """
    def __init__(self):
        self.listeners = []

    def notify(self, *args, **kwargs):
        """
        Notifies all listeners that an event has occured.
        @param args: arbitraty arguments that will be passed to the listeners
        """
        map(lambda listener: listener(*args, **kwargs), self.listeners)

    def subscribe(self, listener):
        """
        Subscribes an event listener, who will receive events from the broadcaster.
        @type listener: function
        """
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        """
        Unsubscribes an event listener.
        It will no longer receive events after he unsubscribes.
        @param listener: function
        """
        self.listeners.remove(listener)

    def clear(self):
        """
        Removes all event listeners.
        """
        self.listeners = []

    def redirect(self, broadcaster):
        """
        Redirects this broadcaster to the given broadcaster.

        All events fired by this broadcaster will be also delivered to the given broadcaster.
        @type broadcaster: EventBroadcaster
        """
        self.subscribe(broadcaster.notify)
