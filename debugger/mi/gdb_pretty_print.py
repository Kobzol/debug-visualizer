import gdb


class Iterator:
    """Compatibility mixin for iterators

    Instead of writing next() methods for iterators, write
    __next__() methods and use this mixin to make them work in
    Python 2 as well as Python 3.

    Idea stolen from the "six" documentation:
    <http://pythonhosted.org/six/#six.Iterator>
    """

    def next(self):
        return self.__next__()


class StdVectorPrinter:
    "Print a std::vector"

    class _iterator(Iterator):
        def __init__ (self, start, finish, bitvec):
            self.bitvec = bitvec
            if bitvec:
                self.item   = start['_M_p']
                self.so     = start['_M_offset']
                self.finish = finish['_M_p']
                self.fo     = finish['_M_offset']
                itype = self.item.dereference().type
                self.isize = 8 * itype.sizeof
            else:
                self.item = start
                self.finish = finish
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            count = self.count
            self.count += 1

            if self.bitvec:
                if self.item == self.finish and self.so >= self.fo:
                    raise StopIteration
                elt = self.item.dereference()
                if elt & (1 << self.so):
                    obit = 1
                else:
                    obit = 0
                self.so = self.so + 1
                if self.so >= self.isize:
                    self.item = self.item + 1
                    self.so = 0
                return ("v{0}".format(count), obit)
            else:
                if self.item == self.finish:
                    raise StopIteration
                elt = self.item.dereference()
                self.item = self.item + 1

                return ("v{0}".format(count), elt)

    def __init__(self, typename, val):
        self.typename = typename
        self.val = val
        self.is_bool = val.type.template_argument(0).code == gdb.TYPE_CODE_BOOL

    def children(self):
        return self._iterator(self.val['_M_impl']['_M_start'],
                              self.val['_M_impl']['_M_finish'],
                              self.is_bool)

    def to_string(self):
        return None

    def display_hint(self):
        return "string"


def str_lookup_function(val):
    if val is None or val.type is None or val.type.name is None:
        return None
    if val.type.name.startswith("std::vector"):
        return StdVectorPrinter("std::vector", val)
    else:
        return None


def register_printers(objfile):
    objfile.pretty_printers.append(str_lookup_function)

gdb.events.new_objfile.connect(lambda event: register_printers(event.new_objfile))