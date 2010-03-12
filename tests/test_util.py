from nose.tools import raises
from crank.util import *

class TestOdict:

    def setup(self):
        self.d = odict()

    def test_create(self):
        pass

    def test_set_item(self):
        self.d['a'] = 1
        assert self.d['a'] == 1

    def test_keys(self):
        self.d['b'] = 1
        self.d['a'] = 1
        assert self.d.keys() == ['b', 'a']

    def test_clear(self):
        self.d['b'] = 1
        self.d['a'] = 1
        self.d.keys() == ['b', 'a']
        self.d.clear()
        assert self.d.keys() == []

#    def test_slice(self):
#        self.d['b'] = 2
#        self.d['a'] = 1
#        self.d[:1] == [2]

    def test_iteritems(self):
        self.d['b'] = 2
        self.d['a'] = 1
        assert [i for i in self.d.iteritems()] == [('b',2), ('a',1)]

    def test_items(self):
        self.d['b'] = 2
        self.d['a'] = 1
        assert self.d.items() == [('b',2), ('a',1)]

    def test_values(self):
        self.d['b'] = 2
        self.d['a'] = 1
        assert self.d.values() == [2,1]

    def test_itervalues(self):
        self.d['b'] = 2
        self.d['a'] = 1
        assert [i for i in self.d.itervalues()] == [2,1]

    @raises(KeyError)
    def test_delete(self):
        self.d['b'] = 2
        del self.d['b']
        assert self.d._ordering == [], self.d._ordering
        self.d['b']

    @raises(KeyError)
    def test_pop(self):
        self.d['b'] = 2
        self.d.pop()
        self.d['b']

    def test__str__(self):
        self.d['b'] = 2
        assert str(self.d) == "[('b', 2)]", str(self.d)

from inspect import ArgSpec

def mock_f(a, b, c=None, d=50, *args, **kw):
    pass

def test_get_argspec_first_call():
    argspec = get_argspec(mock_f)
    assert argspec == ArgSpec(args=['a', 'b', 'c', 'd'], varargs='args', keywords='kw', defaults=(None, 50)), argspec

def test_get_argspec_cached():
    argspec = get_argspec(mock_f)
    assert argspec == ArgSpec(args=['a', 'b', 'c', 'd'], varargs='args', keywords='kw', defaults=(None, 50)), argspec


