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

class MockSubDispatcher(ObjectDispatcher):
    def index(self):
        pass

class MockLookupHelperWithArgs:

    def get_here(self, *args):
        pass

    def post_with_mixed_args(self, arg1, arg2, **kw):
        pass

class MockLoookupDispatcherWithArgs(ObjectDispatcher):

    def _lookup(self, *args):
        return MockLookupHelperWithArgs(), args

mock_lookup_dispatcher_with_args = MockLoookupDispatcherWithArgs()

class MockDispatchDispatcher(ObjectDispatcher):

    def wacky(self, *args, **kw):
        pass

    def _check_security(self):
        pass

    def _dispatch(self, state, remainder=None):
        state.add_method(self.wacky, remainder)
        return state

class MockDispatcher(ObjectDispatcher):


    def index(self):
        pass

    def _default(self, *args, **kw):
        pass

    def no_args(self):
        pass

    def with_args(self, a, b):
        pass

    sub = MockSubDispatcher()
    override_dispatch = MockDispatchDispatcher()

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
    
    def test_call(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher(state, [])
        assert state.method.__name__ == 'index', state.method

    def test_dispatch_index(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state, [])
        assert state.method.__name__ == 'index', state.method

    def test_dispatch_default(self):
        req = MockRequest('/', params={'a':1})
        state = DispatchState(req, self.dispatcher)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_dispatch_default_with_unicode(self):
        req = MockRequest('/', params={u'å':u'ß'})
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_controller_method_dispatch_no_args(self):
        req = MockRequest('/no_args')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'no_args', state.method

    def test_controller_method_with_unicode_args(self):
        req = MockRequest(u'/with_args/å/ß')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'with_args', state.method

    def test_controller_method_with_empty_args(self):
        req = MockRequest('/with_args//a/b')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_controller_method_with_args(self):
        req = MockRequest('/with_args/a/b')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'with_args', state.method

    def test_controller_method_with_args_missing_args_default(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req)
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

    @raises(HTTPNotFound)
    def test_controller_method_with_args_missing_args_index_disabled(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_index_with_argvars)
        
        try:
            mock_dispatcher_with_index_with_argvars._use_index_fallback = False
            state = mock_dispatcher_with_index_with_argvars._dispatch(state)
        finally:
            mock_dispatcher_with_index_with_argvars._use_index_fallback = True

    @raises(MockError)
    def test_check_security(self):
        req = MockRequest('/with_args/a')
        state = DispatchState(req, mock_dispatcher_with_check_security)
        state = mock_dispatcher_with_check_security._dispatch(state)

    def test_sub_dispatcher(self):
        req = MockRequest('/sub')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'index', state.method
        assert state.controller.__class__.__name__ == 'MockSubDispatcher', state.controller

    def test_sub_dispatcher_bad_remainder_call_parent_default(self):
        req = MockRequest('/sub/a')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_sub_dispatcher_bad_params_call_parent_default(self):
        req = MockRequest('/sub', params={'a':1})
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == '_default', state.method

    def test_sub_dispatcher_override_dispatch(self):
        req = MockRequest('/override_dispatch', params={'a':1})
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'wacky', state.method

    def test_lookup_dispatch(self):
        req = MockRequest('/get_here')
        state = DispatchState(req, mock_lookup_dispatcher_with_args)
        state = mock_lookup_dispatcher_with_args._dispatch(state)
        assert state.method.__name__ == 'get_here', state.method
        assert state.controller.__class__.__name__ == 'MockLookupHelperWithArgs', state.controller

    @raises(HTTPNotFound)
    def test_lookup_dispatch_bad_params(self):
        req = MockRequest('/get_here', params={'a':1})
        state = DispatchState(req, mock_lookup_dispatcher_with_args)
        state = mock_lookup_dispatcher_with_args._dispatch(state)
