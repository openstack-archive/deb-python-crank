"""
This is the main dispatcher module.

Dispatch works as follows:
Start at the RootController, the root controller must
have a _dispatch function, which defines how we move
from object to object in the system.
Continue following the dispatch mechanism for a given
controller until you reach another controller with a
_dispatch method defined.  Use the new _dispatch
method until anther controller with _dispatch defined
or until the url has been traversed to entirety.

This module also contains the standard ObjectDispatch
class which provides the ordinary TurboGears mechanism.

"""

class odict(dict):

    def __init__(self, *args, **kw):
        self._ordering = []
        dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        self._ordering.append(key)
        dict.__setitem__(self, key, value)

    def keys(self):
        return self._ordering

    def clear(self):
        self._ordering = []
        dict.clear(self)

    def getitem(self, n):
        return self[self._ordering[n]]

    def __slice__(self, a, b, n):
        return self.values()[a:b:n]

    def iteritems(self):
        for item in self._ordering:
            yield item, self[item]

    def items(self):
        return [i for i in self.iteritems()]

    def itervalues(self):
        for item in self._ordering:
            yield self[item]

    def values(self):
        return [i for i in self.values()]

    def __delete__(self, key):
        self._ordering.remove(key)
        dict.__delete__(self, key)

    def pop(self):
        item = self._ordering[-1]
        del self[item]
        self._ordering.remove(item)

    def __str__(self):
        return str(self.items())

