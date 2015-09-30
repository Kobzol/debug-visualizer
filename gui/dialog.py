from gi.repository import Gtk 


class FileOpenDialog(object):
    @staticmethod
    def open_file(title, parent):
        dialog = FileOpenDialog(title, parent)
        
        file = dialog.open()
        dialog.destroy()
        
        return file
    
    def __init__(self, title, parent):
        self.dialog = Gtk.FileChooserDialog(title, parent,
                                    Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
               
    def open(self):
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            return self.dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            return None
            
    def destroy(self):
        self.dialog.destroy()


class MessageBox(Gtk.MessageDialog):
    @staticmethod
    def show(text, title, parent, msg_type=Gtk.MessageType.ERROR):
        dialog = Gtk.MessageDialog(parent, 0, msg_type, Gtk.ButtonsType.CLOSE, text=text, title=title)
        dialog.connect("response", lambda widget, response: widget.destroy())
        dialog.show_all()
