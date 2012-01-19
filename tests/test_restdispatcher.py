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

class MockEmbeddedRestDispatcherWithArgs(RestDispatcher):

    def get_one(self, mock_id):
        pass
    def post(self, mock_id):
        pass
    def put(self, mock_id):
        pass
    def delete(self, mock_id):
        pass

class MockDispatcherWithArgs(RestDispatcher):

    def post(self, arg1, **kw):
        pass
    def other(self, *args):
        pass
    sub = MockEmbeddedRestDispatcherWithArgs()


class MockDispatcherWithVarArgs(RestDispatcher):
    def get_one(self, *crazy_args):
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

class MockMinimalRestDispatcher(RestDispatcher):
    def get_one(self):
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

class TestMinimalRestDispatcher:

    def setup(self):
        self.dispatcher = MockMinimalRestDispatcher()

    def test_create(self):
        pass

    def test_get_all_fallback_on_get_one(self):
        req = MockRequest('/')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_one'

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
        req = MockRequest('/sub/asdf', method='put')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'put', state.method

    def test_delete(self):
        req = MockRequest('/sub/asdf', method='delete')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'delete', state.method

    def test_other(self):
        req = MockRequest('/other', method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'other'

    @raises(HTTPNotFound)
    def test_post_bad(self):
        req = MockRequest('/aaa/aaa', method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'pos', state.method

    @raises(HTTPMethodNotAllowed)
    def test_other_delete_bad(self):
        req = MockRequest('/other/asdf', method='delete')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'other'

    @raises(HTTPNotFound)
    def test_other_delete_not_found(self):
        req = MockRequest('/not_found', method='delete')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'other'

    def test_sub_get_one(self):
        req = MockRequest('/sub/mid', method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_one'


class TestDispatcherWithVarArgs:

    def setup(self):
        self.dispatcher = MockDispatcherWithVarArgs()

    def test_create(self):
        pass

    def test_delete(self):
        req = MockRequest('/asdf1/asdf2/asdf3/asdf4/sub')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_all', state.method

class MockCustomMethodDispatcher(RestDispatcher):

    _custom_actions = ['custom']

    def get_custom(self):
        pass

    def post_custom(self):
        pass

class TestCustomMethodDispatcher:

    def setup(self):
        self.dispatcher = MockCustomMethodDispatcher()

    def test_create(self):
        pass

    def test_post(self):
        req = MockRequest('/', method='custom')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post_custom', state.method

    def test_post_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='post')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'post_custom', state.method

    def test_get_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_custom', state.method

    def test_get_url(self):
        req = MockRequest('/custom')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_custom', state.method

    @raises(HTTPNotFound)
    def test_get_fail(self):
        req = MockRequest('/not_found', params={'_method':'custom'}, method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_custom', state.method

class SubCustomMethodDispatcher(MockDispatcher):

    sub = MockCustomMethodDispatcher()

class TestSubCustomMethodDispatcher:

    def setup(self):
        self.dispatcher = SubCustomMethodDispatcher()

    def test_create(self):
        pass

    def test_get_url(self):
        req = MockRequest('/sub', params={'_method':'custom'}, method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
        assert state.method.__name__ == 'get_custom', state.method

class SubNoGet(RestDispatcher):
    pass

class OtherSubCustomMethodDispatcher(MockDispatcher):
    sub = SubNoGet()

class TestSubNoGetDispatcher:

    def setup(self):
        self.dispatcher = OtherSubCustomMethodDispatcher()

    def test_create(self):
        pass

    @raises(HTTPNotFound)
    def test_get_not_found(self):
        req = MockRequest('/sub', method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)

class TestEmptyDispatcher:
    def setup(self):
        self.dispatcher = SubNoGet()

    def test_create(self):
        pass

    @raises(HTTPNotFound)
    def test_get_not_found(self):
        req = MockRequest('/sub', method='get')
        state = DispatchState(req)
        state = self.dispatcher._dispatch(state)
