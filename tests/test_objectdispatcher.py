# encoding: utf-8
from nose.tools import raises
from crank.objectdispatcher import *
from crank.dispatchstate import DispatchState
from webob.exc import HTTPNotFound

class MockRequest(object):

    def __init__(self, path_info, params=None):
        self.path_info = path_info
        self.params = params
        if params is None:
            self.params = {}

class MockDispatcher(ObjectDispatcher):

    def index(self):
        pass

    def _default(self, *args, **kw):
        pass

    def no_args(self):
        pass

    def with_args(self, a, b):
        pass

class MockError(Exception):pass
class MockDispatcherWithSecurity(ObjectDispatcher):
    def _check_security(self):
        raise MockError
    def _default(self, *args, **kw):
        pass

mock_dispatcher_with_check_security = MockDispatcherWithSecurity()

class MockDispatcherWithNoDefaultOrIndex(ObjectDispatcher):

    def no_args(self):
        pass

    def with_args(self, a, b):
        pass

mock_dispatcher_with_no_default_or_index = MockDispatcherWithNoDefaultOrIndex()

class MockDispatcherWithNoDefault(ObjectDispatcher):
    def index(self):
        pass

mock_dispatcher_with_no_default = MockDispatcherWithNoDefault()

class MockDispatcherWithIndexWithArgVars(ObjectDispatcher):
    def index(self, *args):
        pass

mock_dispatcher_with_index_with_argvars = MockDispatcherWithIndexWithArgVars()

class MockDispatcherWithNoIndex(ObjectDispatcher):
    def _default(self):
        pass

mock_dispatcher_with_no_index = MockDispatcherWithNoIndex()

class TestDispatcher:

    def setup(self):
        self.dispatcher = MockDispatcher()

    def test_create(self):
        pass

    def test_dispatch_index(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state, [])
        assert state.method.__name__ == 'index', state.method

    def test_dispatch_default(self):
        req = MockRequest('/', params={'a':1})
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_dispatch_default_with_unicode(self):
        req = MockRequest('/', params={u'å':u'ß'})
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_controller_method_dispatch_no_args(self):
        req = MockRequest('/no_args')
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'no_args', state.method

    def test_controller_method_with_unicode_args(self):
        req = MockRequest(u'/with_args/å/ß')
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'with_args', state.method

    def test_controller_method_with_args(self):
        req = MockRequest('/with_args/a/b')
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'with_args', state.method

    def test_controller_method_with_args_missing_args_default(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    @raises(HTTPNotFound)
    def test_controller_method_with_args_missing_args_404_default_or_index(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_no_default_or_index)
        state = mock_dispatcher_with_no_default_or_index._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    @raises(HTTPNotFound)
    def test_controller_method_with_args_missing_args_404_no_default(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_no_default)
        state = mock_dispatcher_with_no_default_or_index._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_controller_method_with_args_missing_args_index(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_index_with_argvars)
        state = mock_dispatcher_with_index_with_argvars._dispatch(state)
        assert state.method.__name__ == 'index', state.method

    @raises(MockError)
    def test_check_security(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_check_security)
        state = mock_dispatcher_with_check_security._dispatch(state)
