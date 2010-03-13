from nose.tools import raises
from crank.objectdispatcher import *
from crank.dispatchstate import DispatchState

class MockRequest(object):
    path_info = 'something'
    params = {'c':3, 'd':4}

class MockDispatcher(ObjectDispatcher):

    def index(self, *args, **kw):
        return 'here'

mock_request = MockRequest()

class TestDispatcher:

    def setup(self):
        self.dispatcher = MockDispatcher()

    def test_create(self):
        pass

    def test_dispatch(self):
        state = DispatchState(mock_request, self.dispatcher)
        state = self.dispatcher._dispatch(state, [])
        assert state.method.__name__ == 'index', state.method
