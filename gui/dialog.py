# -*- coding: utf-8 -*-

from gi.repository import Gtk

from gui_util import require_gui_thread


class FileOpenDialog(object):
    @staticmethod
    @require_gui_thread
    def select_file(title, parent, initial_path=None):
        """
        @type title: str
        @type parent: Gtk.Widget
        @type initial_path: str
        @rtype: str
        """
        dialog = FileOpenDialog(title, parent, False, initial_path)

        file = dialog.open()
        dialog.destroy()

        return file

    @staticmethod
    @require_gui_thread
    def select_folder(title, parent, initial_path=None):
        """
        @type title: str
        @type parent: Gtk.Widget
        @type initial_path: str
        @rtype: str
        """
        dialog = FileOpenDialog(title, parent, True, initial_path)

        folder = dialog.open()
        dialog.destroy()

        return folder

    def __init__(self, title, parent, directory=False, initial_path=None):
        """
        Opens a file or folder chooser dialog.
        @type title: str
        @type parent: Gtk.Widget
        @type directory: bool
        @type initial_path: str
        """
        type = Gtk.FileChooserAction.OPEN

        if directory:
            type = Gtk.FileChooserAction.SELECT_FOLDER

        self.dialog = Gtk.FileChooserDialog(title, parent,
                                            type,
                                            (Gtk.STOCK_CANCEL,
                                             Gtk.ResponseType.CANCEL,
                                             Gtk.STOCK_OPEN,
                                             Gtk.ResponseType.OK))

        if initial_path:
            self.dialog.set_current_folder(initial_path)

    @require_gui_thread
    def open(self):
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            return self.dialog.get_filename()
        else:
            return None

    @require_gui_thread
    def destroy(self):
        self.dialog.destroy()


class MessageBox(Gtk.MessageDialog):
    @staticmethod
    @require_gui_thread
    def show(text, title, parent, msg_type=Gtk.MessageType.ERROR):
        dialog = Gtk.MessageDialog(parent, 0, msg_type, Gtk.ButtonsType.CLOSE,
                                   text=text, title=title)
        dialog.connect("response", lambda widget, response: widget.destroy())
        dialog.show_all()
