# encoding: utf-8
from nose.tools import raises
from crank.restdispatcher import RestDispatcher
from crank.objectdispatcher import ObjectDispatcher
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

class MockError(Exception):pass
class MockRestDispatcherWithSecurity(RestDispatcher):
    def _check_security(self):
        raise MockError

    def get_one(self, *args):
        pass

class MockRestDispatcherWithNestedSecurity(RestDispatcher):
    withsec = MockRestDispatcherWithSecurity()

    def get_all(self, *args):
        pass

class MockDispatcherWithLookupOnSecurity(ObjectDispatcher):
    def _lookup(self, *args):
        if 'direct' in args:
            return MockRestDispatcherWithSecurity(), args[1:]
        if 'nested' in args:
            return MockRestDispatcherWithNestedSecurity(), args[1:]

class TestDispatcher:

    def setup(self):
        self.dispatcher = MockDispatcher()

    def test_create(self):
        pass

    def test_get_all(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_all'

    def test_get_one(self):
        req = MockRequest('/asdf')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_one'
        assert state.params == {}, state.params
        assert state.remainder == ['asdf'], state.remainder

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post'

    def test_post_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post_delete'

    def test_post_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post_delete'

    def test_get_delete(self):
        req = MockRequest('/delete', method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_delete'

    @raises(HTTPMethodNotAllowed)
    def test_delete_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'delete'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

    @raises(HTTPMethodNotAllowed)
    def test_put_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'put'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

    def test_put(self):
        req = MockRequest('/', params={'_method':'put'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'put', state.method

    def test_put(self):
        req = MockRequest('/', method='put')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'put', state.method

    def test_other_method(self):
        req = MockRequest('/other')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'other', state.method

class TestSimpleDispatcher:

    def setup(self):
        self.dispatcher = MockSimpleDispatcher()

    def test_get(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get'

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post'

    def test_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'delete'

    def test_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'delete'

class TestEmbeddedRestDispatcher:

    def setup(self):
        self.dispatcher = MockEmbeddedRestDispatcher()

    def test_create(self):
        pass

    def test_delete_hacky(self):
        req = MockRequest('/asdf/sub', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
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
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_one'

class TestDispatcherWithArgs:

    def setup(self):
        self.dispatcher = MockDispatcherWithArgs()

    def test_create(self):
        pass

    def test_post(self):
        req = MockRequest('/asdf', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post'

    def test_put(self):
        req = MockRequest('/sub/asdf', method='put')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'put', state.method

    def test_delete(self):
        req = MockRequest('/sub/asdf', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'delete', state.method

    def test_other(self):
        req = MockRequest('/other', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'other'

    def test_other_with_get_method(self):
        req = MockRequest('/other/something', params={'_method':'get'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'other', state.method

    @raises(HTTPNotFound)
    def test_post_bad(self):
        req = MockRequest('/aaa/aaa', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'pos', state.method

    @raises(HTTPMethodNotAllowed)
    def test_other_delete_bad(self):
        req = MockRequest('/other/asdf', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'other'

    @raises(HTTPNotFound)
    def test_other_delete_not_found(self):
        req = MockRequest('/not_found', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'other'

    def test_sub_get_one(self):
        req = MockRequest('/sub/mid', method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_one'


class TestDispatcherWithVarArgs:

    def setup(self):
        self.dispatcher = MockDispatcherWithVarArgs()

    def test_create(self):
        pass

    def test_delete(self):
        req = MockRequest('/asdf1/asdf2/asdf3/asdf4/sub')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
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
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post_custom', state.method

    def test_post_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'post_custom', state.method

    def test_get_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_custom', state.method

    def test_get_url(self):
        req = MockRequest('/custom')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.method.__name__ == 'get_custom', state.method

    @raises(HTTPNotFound)
    def test_get_fail(self):
        req = MockRequest('/not_found', params={'_method':'custom'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
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
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
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
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

class TestEmptyDispatcher:
    def setup(self):
        self.dispatcher = SubNoGet()

    def test_create(self):
        pass

    @raises(HTTPNotFound)
    def test_get_not_found(self):
        req = MockRequest('/sub', method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

class TestRestWithSecurity:
    def setup(self):
        self.dispatcher = MockDispatcherWithLookupOnSecurity()

    @raises(MockError)
    def test_check_security_with_lookup(self):
        req = MockRequest('/direct/a')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

    @raises(MockError)
    def test_check_security_with_nested_lookup(self):
        req = MockRequest('/nested/withsec/a')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()

class TestRestWithLookup:
    class RootController(ObjectDispatcher):
        class rest(RestDispatcher):
            class sub(ObjectDispatcher):
                def method(self):
                    pass
            sub = sub()

            def get(self, itemid):
                return str(itemid)

            def _lookup(self, *args, **kw):
                return self.sub, args[1:]
        rest = rest()

    def setup(self):
        self.dispatcher = self.RootController()

    def test_rest_with_lookup(self):
        req = MockRequest('/rest/somethingelse/method')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'sub', state.controller
        assert state.method.__name__ == 'method', state.method

    def test_rest_lookup_doesnt_mess_with_get(self):
        req = MockRequest('/rest/25')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'rest', state.controller
        assert state.method.__name__ == 'get', state.method

    def test_rest_lookup_doesnt_mess_with_subcontroller(self):
        req = MockRequest('/rest/sub/method')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'sub', state.controller
        assert state.method.__name__ == 'method', state.method

class TestRestCheckSecurity:
    class RootController(ObjectDispatcher):
        class rest(RestDispatcher):
            def _check_security(self):
                self.trace_security_visits.append(True)
                return True

            def get(self, itemid):
                return str(itemid)

        rest = rest()

    def setup(self):
        self.security_tracing = []
        self.dispatcher = self.RootController()
        self.dispatcher.rest.trace_security_visits = self.security_tracing

    def test_rest_security_check_only_once(self):
        req = MockRequest('/rest/25')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'rest', state.controller
        assert state.method.__name__ == 'get', state.method
        assert len(self.security_tracing) == 1, self.security_tracing