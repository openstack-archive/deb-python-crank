# encoding: utf-8
from nose.tools import raises
from crank.restdispatcher import RestDispatcher
from crank.dispatchstate import DispatchState
from webob.exc import HTTPNotFound

class MockRequest(object):

    def __init__(self, path, method='GET', params=None):
        self.path_info = path
        self.params = params
        if params is None:
            self.params = {}
        self.method = method

class MockDispatcher(RestDispatcher):

    def get_one(self, mock_id):
        pass

    def get_all(self):
        pass

class MockSimpleDispatcher(RestDispatcher):

    def get(self):
        pass

class TestDispatcher:

    def setup(self):
        self.dispatcher = MockDispatcher()

    def test_create(self):
        pass

    def test_get_all(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_all'

    def test_get_one(self):
        req = MockRequest('/asdf')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_one'
        assert state.params == {}, state.params
        assert state.remainder == ['asdf'], state.remainder

class TestSimpleDispatcher:

    def setup(self):
        self.dispatcher = MockSimpleDispatcher()

    def test_get(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get'

