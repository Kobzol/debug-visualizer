from gi.repository import Gtk

from gui_util import require_gui_thread


class FileOpenDialog(object):
    @staticmethod
    @require_gui_thread
    def open_file(title, parent, initial_path=None):
        dialog = FileOpenDialog(title, parent, initial_path)
        
        file = dialog.open()
        dialog.destroy()
        
        return file
    
    def __init__(self, title, parent, initial_path=None):
        self.dialog = Gtk.FileChooserDialog(title, parent,
                                    Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

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
        dialog = Gtk.MessageDialog(parent, 0, msg_type, Gtk.ButtonsType.CLOSE, text=text, title=title)
        dialog.connect("response", lambda widget, response: widget.destroy())
        dialog.show_all()
