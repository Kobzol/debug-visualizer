class IOHelper(object):
    @staticmethod
    def load_file(path):
        try:
            data = open(path).read()
        except:
            return None