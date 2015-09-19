from gi.repository import GtkSource

class SourceEditor(object):
    @staticmethod
    def load_file(path):
        try:
            return open(path).read()
        except:
            return None
    
    def __init__(self, language="cpp"):
        self.buffer = GtkSource.Buffer()
        self.start_undoable()
        self.set_language(language)
        self.buffer.set_highlight_syntax(True)
        self.buffer.set_highlight_matching_brackets(True)
        self.stop_undoable()
        
        self.view = GtkSource.View.new_with_buffer(self.buffer)
        self.view.set_show_line_numbers(True)
        self.view.set_highlight_current_line(True)
        self.view.set_show_right_margin(True)
        self.view.set_right_margin_position(80)
        
    def get_view(self):
        return self.view
    
    def set_language(self, key):
        manager = GtkSource.LanguageManager()
        language = manager.get_language(key)
        self.buffer.set_language(language)
    
    def start_undoable(self):
        self.buffer.begin_not_undoable_action()
        
    def stop_undoable(self):
        self.buffer.end_not_undoable_action()
        
    def set_content_from_file(self, path):
        content = SourceEditor.load_file(path)
        
        if content:
            self.start_undoable()
            self.buffer.set_text(content)
            self.stop_undoable()
    
    