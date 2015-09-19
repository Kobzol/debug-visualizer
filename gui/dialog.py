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