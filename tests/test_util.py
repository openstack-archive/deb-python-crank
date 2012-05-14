# encoding: utf-8
import sys
from nose.tools import raises
from crank.util import *

_PY3 = bool(sys.version_info[0] == 3)
if _PY3:
    def u(s): return s
else:
    def u(s): return s.decode('utf-8')

def mock_f(self, a, b, c=None, d=50, *args, **kw):
    pass

def test_get_argspec_first_call():
    argspec = get_argspec(mock_f)
    assert argspec == (['a', 'b', 'c', 'd'], 'args', 'kw', (None, 50)), argspec

def test_get_argspec_cached():
    argspec = get_argspec(mock_f)
    assert argspec == (['a', 'b', 'c', 'd'], 'args', 'kw', (None, 50)), argspec

def test_get_params_with_argspec():
    params = get_params_with_argspec(mock_f, {'a':1, 'c':2}, [3])
    assert params == {'a': 3, 'c': 2}, params

def test_remove_argspec_params_from_params():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2}, [3])
    assert params == {}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_remove_optional_positionals():
    params, remainder = remove_argspec_params_from_params(mock_f, {'c':45}, [3, 3, 4])
    assert params == {}, params
    assert remainder == (3, 3, 45), repr(remainder)

def test_remove_argspec_params_from_params_none_remainder():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2}, None)
    assert params == {'a': 1, 'b': 2}, params
    assert remainder == None, repr(remainder)

def mock_f2(self, a, b):
    pass

def test_remove_argspec_params_from_params_in_remainder():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'b':1}, ['a'])
    assert params == {}, params
    assert remainder == ('a', 1,), repr(remainder)


def test_remove_argspec_params_from_params_no_conditionals():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a'])
    assert params == {}, params
    assert remainder == (1,2), repr(remainder)

def test_remove_argspec_params_from_params_req_var_in_params():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a'])
    assert params == {}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_avoid_creating_duplicate_parameters():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2, 'c':3}, ['a', 'b'])
    assert params == {'c': 3}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_avoid_duplicate_params():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a', 'b'])


def test_method_matches_args_no_remainder():
    params = {'a':1, 'b':2, 'c':3}
    remainder = []
    r = method_matches_args(mock_f, params, remainder)
    assert r

def test_method_matches_args_no_lax_params():
    params = {'a':1, 'b':2, 'c':3, 'x':4}
    remainder = []
    r = method_matches_args(mock_f2, params, remainder, False)
    assert not(r)

def test_method_matches_args_fails_no_remainder():
    params = {'a':1, 'x':3}
    remainder = []
    r = method_matches_args(mock_f, params, remainder)
    assert not(r)

def test_method_matches_args_no_params():
    params = {}
    remainder = [1, 2]
    r = method_matches_args(mock_f, params, remainder)
    assert r

def test_method_matches_args_fails_no_params():
    params = {}
    remainder = [2]
    r = method_matches_args(mock_f, params, remainder)
    assert not(r)

def test_method_matches_args_fails_no_params():
    params = {}
    remainder = [2]
    r = method_matches_args(mock_f2, params, remainder)
    assert not(r)

def test_method_matches_args_fails_more_remainder_than_argspec():
    params = {}
    remainder = [2, 3, 4, 5]
    r = method_matches_args(mock_f2, params, remainder)
    assert not(r)

def mock_f3(self, a, b, c=None, d=50):
    pass

def test_method_matches_args_with_default_values():
    params = {'a':1, 'b':2, 'c':3, 'd':4}
    remainder = []
    r = method_matches_args(mock_f3, params, remainder)
    assert r

def assert_path(instance, expected, kind=list):
    assert kind(instance.path) == expected, (kind(instance.path), expected)

def test_path_path():
    assert Path(Path('/foo')) == ['', 'foo']

def test_path_list():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', ['', '']),
            ('/foo', ['', 'foo']),
            ('/foo/bar', ['', 'foo', 'bar']),
            ('/foo/bar/', ['', 'foo', 'bar', '']),
            ('/foo//bar/', ['', 'foo', '', 'bar', '']),
            (('foo', ), ['foo']),
            (('foo', 'bar'), ['foo', 'bar'])
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case
        
        yield assert_path, instance, expected

def test_path_str():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', "/"),
            ('/foo', '/foo'),
            ('/foo/bar', '/foo/bar'),
            ('/foo/bar/', '/foo/bar/'),
            ('/foo//bar/', '/foo//bar/'),
            (('foo', ), 'foo'),
            (('foo', 'bar'), 'foo/bar')
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case
        
        yield assert_path, instance, expected, str
    
    instance = MockOb()
    instance.path = '/foo/bar'
    yield assert_path, instance, """<Path "deque([\'\', \'foo\', \'bar\'])">""", repr

def test_path_unicode():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', "/"),
            (u('/©'), u('/©')),
            (u('/©/™'), u('/©/™')),
            (u('/©/™/'), u('/©/™/')),
            ((u('¡'), ), u('¡')),
            (('foo', u('¡')), u('foo/¡'))
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case

        if _PY3:
            yield assert_path, instance, expected, str
        else:
            yield assert_path, instance, expected, unicode

def test_path_slicing():
    class MockOb(object):
        path = Path()
    
    instance = MockOb()
    
    instance.path = '/foo/bar/baz'
    
    assert str(instance.path[1:]) == 'foo/bar/baz'
    assert str(instance.path[2:]) == 'bar/baz'
    assert str(instance.path[0:2]) == '/foo'
    assert str(instance.path[::2]) == '/bar'

def test_path_comparison():
    assert Path('/foo') == ('', 'foo'), 'tuple comparison'
    assert Path('/foo') == ['', 'foo'], 'list comparison'
    assert Path('/foo') == '/foo', 'string comparison'
    assert Path(u('/föö')) == u('/föö'), 'string comparison'
