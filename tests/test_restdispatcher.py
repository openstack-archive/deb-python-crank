# encoding: utf-8
from nose.tools import raises
from crank.restdispatcher import RestDispatcher
from crank.dispatchstate import DispatchState
from webob.exc import HTTPNotFound, HTTPMethodNotAllowed

class MockRequest(object):

    def __init__(self, path, method='GET', params=None):
        self.path_info = path
        self.params = params
        if params is None:
            self.params = {}
        self.method = method

class MockDispatcher(RestDispatcher):

    def post(self):
        pass

    def put(self):
        pass

    def post_delete(self):
        pass

    def get_delete(self):
        pass

    def get_one(self, mock_id):
        pass

    def get_all(self):
        pass

    def other(self):
        pass

class MockDispatcherWithArgs(RestDispatcher):

    def post(self, *args, **kw):
        pass

    def other(self, *args):
        pass
    sub = MockDispatcher()

class MockEmbeddedRestDispatcher(RestDispatcher):
    def get_one(self, mock_id):
        pass
    sub = MockDispatcher()


class MockSimpleDispatcher(RestDispatcher):

    def get(self):
        pass

    def post(self):
        pass

    def delete(self):
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

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post'

    def test_post_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post_delete'

    def test_post_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post_delete'

    def test_get_delete(self):
        req = MockRequest('/delete', method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_delete'

    @raises(HTTPMethodNotAllowed)
    def test_delete_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'delete'}, method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)

    @raises(HTTPMethodNotAllowed)
    def test_put_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'put'}, method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)

    def test_put(self):
        req = MockRequest('/', params={'_method':'put'}, method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'put', state.method

    def test_put(self):
        req = MockRequest('/', method='put')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'put', state.method

    def test_other_method(self):
        req = MockRequest('/other')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'other', state.method

class TestSimpleDispatcher:

    def setup(self):
        self.dispatcher = MockSimpleDispatcher()

    def test_get(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get'

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post'

    def test_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'delete'

    def test_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'delete'

class TestEmbeddedRestDispatcher:

    def setup(self):
        self.dispatcher = MockEmbeddedRestDispatcher()

    def test_create(self):
        pass

    def test_delete_hacky(self):
        req = MockRequest('/asdf/sub', params={'_method':'delete'}, method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post_delete', state.method
        assert state.controller.__class__.__name__ == 'MockDispatcher', state.controller
        assert state.params == {}, state.params

class TestDispatcherWithArgs:

    def setup(self):
        self.dispatcher = MockDispatcherWithArgs()

    def test_create(self):
        pass

    def test_post(self):
        req = MockRequest('/asdf', method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post'

    def test_put(self):
        req = MockRequest('/sub')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_all', state.method

    def test_other(self):
        req = MockRequest('/other')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'other'
