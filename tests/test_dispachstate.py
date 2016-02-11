from crank.dispatchstate import DispatchState

class MockRequest(object):
    path_info = 'something'
    params = {'c':3, 'd':4}

class MockController(object):
    pass

class TestDispatchState:

    def setup(self):
        self.request = MockRequest()
        self.dispatcher = MockController()
        self.state = DispatchState(self.request, self.dispatcher, {'a':1, 'b':2})

    def test_create(self):
        assert self.state.params == {'a':1, 'b':2}, self.state.params
        assert self.state.root_dispatcher == self.dispatcher
        assert self.state.routing_args == {}

    def test_create_params_in_request(self):
        state = DispatchState(self.request, self.dispatcher)
        assert state.params == {'c':3, 'd':4}, state.params

    def test_add_controller(self):
        mock = MockController()
        self.state.add_controller('mock', mock)
        assert dict(self.state.controller_path)['mock'] == mock

    def test_add_method(self):
        self.state.add_method('a', 'b')
        assert self.state.method == 'a'
        assert self.state.remainder == 'b'
        
    def test_use_path_info(self):
        state = DispatchState(self.request, self.dispatcher, path_info=['a', 'b'])
        assert state.path == ['a', 'b'], state.path

    def test_ignore_parameters(self):
        state = DispatchState(self.request, self.dispatcher, {'a':1, 'z':5}, ignore_parameters=['z'])
        assert state.params == {'a':1}, state.params
        
    def test_path_info_with_blanks(self):
        state = DispatchState(self.request, self.dispatcher, path_info=['', 'a', 'b', '',''])
        assert state.path == ['a', 'b'], state.path

    def test_path_info_blank(self):
        state = DispatchState(self.request, self.dispatcher, path_info=[])
        assert state.path == [], state.path

    def test_add_routing_args(self):
        current_path = 'current'
        remainder = ['c', 'd']
        fixed = ['e', 'f', 'g']
        var_args = ['g', 'h']
        self.state.add_routing_args(current_path, remainder, fixed, var_args)

    def test_add_routing_args_with_remainder(self):
        current_path = 'current'
        remainder = ['c', 'd', 'x','y']
        fixed = ['e', 'f', 'g']
        var_args = ['g', 'h']
        self.state.add_routing_args(current_path, remainder, fixed, var_args)

    def test_controller(self):
        mock = MockController()
        self.state.add_controller('mock', mock)
        assert self.state.controller == mock
        
    def test_init_with_extension(self):
        r = MockRequest()
        r.path_info = 'something.json'
        state = DispatchState(r, dispatcher=None)
        assert state.extension == 'json'
        
    def test_init_with_string_path(self):
        r = MockRequest()
        r.path_info = 'something.json'
        state = DispatchState(r, dispatcher=None, path_info='s1/s2')
        assert state.path == ['s1', 's2']

