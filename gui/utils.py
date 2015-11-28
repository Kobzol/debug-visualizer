from gi.repository import GObject


def run_on_gui(function, *args):
    GObject.idle_add(lambda *x: function(*args))
