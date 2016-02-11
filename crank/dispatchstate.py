"""
This module implements the :class:`DispatchState` class
"""
import warnings

from crank.util import default_path_translator, noop_translation

try:
    string_type = basestring
except NameError: # pragma: no cover
    string_type = str


class DispatchState(object):
    """
    This class keeps around all the pertainent info for the state
    of the dispatch as it traverses through the tree.  This allows
    us to attach things like routing args and to keep track of the
    path the controller takes along the system.
    
    Arguments:
        request 
              object, must have a path_info attribute if path_info is not provided
        dispatcher
              dispatcher object to get the ball rolling
        params
              parameters to pass into the dispatch state will use request.params
        path_info
              pre-split list of path elements, will use request.pathinfo if not used
        strip_extension
              Whenever crank should strip the url extension or not resolving the path
        path_translator
              Function used to perform path escaping when looking for controller methods,
              can be None to perform no escaping or True to use default escaping function.
    """

    def __init__(self, request, dispatcher, params=None, path_info=None,
                 ignore_parameters=None, strip_extension=True, path_translator=None):
        self._request = request

        if path_translator is None:
            path_translator = noop_translation
        elif path_translator is True:
            path_translator = default_path_translator
        self._path_translator = path_translator

        self._strip_extension = strip_extension
        self.set_path(path_info)

        self._ignored_parameters = ignore_parameters
        if params is None:
            params = request.params
        self.set_params(params)

        self._root_dispatcher = dispatcher
        self._controller = None
        self._controller_path = []
        self._routing_args = {}
        self._action = None
        self._remainder = None
        self._notfound_stack = []

        self.add_controller('/', dispatcher)

    @property
    def root_dispatcher(self):
        """Root Dispatcher instance that initiated the dispatch flow"""
        return self._root_dispatcher

    @property
    def request(self):
        """The request that originated the dispatch process"""
        return self._request

    @property
    def path(self):
        """The path (URL) that has to be dispatched"""
        return self._path

    @property
    def extension(self):
        """Extension of the URL (only if strip_extension is enabled).

        If the path ends with an extension and strip_extension is enabled
        the extension is stripped from the url and is available here.
        """
        return self._extension

    @property
    def controller(self):
        """Controller currently handling the request"""
        return self._controller

    @property
    def controller_path(self):
        """Controllers that got traversed to dispatch the request"""
        return tuple(self._controller_path)

    @property
    def action(self):
        """Method in charge of processing the request"""
        return self._action

    @property
    def params(self):
        """Parameters passed to the action"""
        return self._params

    @property
    def remainder(self):
        """Part of the URL path remaining after lookup of the action.

        Those is usually passed as positional arguments to the method
        in charge of the action together with params.
        """
        return self._remainder

    def add_controller(self, location, controller):
        """Add a controller object to the stack"""
        self._controller = controller
        self._controller_path.append((location, controller))

    def set_action(self, method, remainder):
        """Add the final method that will be called in the _call method"""
        self._action = method
        self._remainder = remainder

    def set_params(self, params):
        """Set parameters that will be passed to the called action"""
        self._params = params
        if self._ignored_parameters:
            for param in self._ignored_parameters:
                self._params.pop(param, None)

    def set_path(self, path_info):
        """Update path that needs to be dispatched.

        In case this is changed during the dispatch process it won't
        have any effect on the dispatch currently under execution.
        """
        path = path_info
        if path is None:
            path = self._request.path_info[1:]
            path = path.split('/')
        elif isinstance(path, string_type):
            path = path.split('/')

        try:
            if not path[0]:
                path = path[1:]
        except IndexError:
            pass

        try:
            while not path[-1]:
                path = path[:-1]
        except IndexError:
            pass

        # rob the extension
        self._extension = None
        if self._strip_extension and len(path) > 0 and '.' in path[-1]:
            end = path[-1]
            end, ext = end.rsplit('.', 1)
            self._extension = ext
            path[-1] = end
        self._path = path

    def resolve(self):
        """Once a DispatchState is created resolving it performs the dispatch.

        Returns the updated DispatchState where ``.controller``, ``.action``,
        ``.params`` and ``.remainder`` properties all point to the controller
        and method that should process the request and to the method arguments.
        """
        if self._action is not None:
            raise RuntimeError('Trying to resolve an already resolved DispatchState')
        return self._root_dispatcher._dispatch(self, self._path)

    def translate_path_piece(self, path_piece):
        return self._path_translator(path_piece=path_piece)

    def add_routing_args(self, current_path, remainder, fixed_args, var_args):
        """
        Add the "intermediate" routing args for a given controller mounted
        at the current_path. This is mostly used during REST dispatch to keep
        track of intermediate arguments and make them always available.
        """
        i = 0
        for i, arg in enumerate(fixed_args):
            if i >= len(remainder):
                break
            self._routing_args[arg] = remainder[i]
        remainder = remainder[i:]
        if var_args and remainder:
            self._routing_args[current_path] = remainder

    @property
    def routing_args(self):
        """Parameters detected by the routing system.

        This includes Request parameters and parameters extracted in other
        ways (usually added through :meth:`.add_routing_args`). In case
        of REST it will include intermediate arguments retrieved during dispatch
        of parent controllers.
        """
        return self._routing_args

    def add_method(self, method, remainder):  # pragma: no cover
        warnings.warn("add_method is deprecated, please use set_action instead",
                      DeprecationWarning, stacklevel=2)
        self.set_action(method, remainder)

    @property
    def method(self):  # pragma: no cover
        warnings.warn(".method is deprecated, please use .action instead",
                      DeprecationWarning, stacklevel=2)
        return self.action

    @property
    def dispatcher(self):  # pragma: no cover
        warnings.warn(".dispatcher is deprecated, please use .root_dispatcher instead",
                      DeprecationWarning, stacklevel=2)
        return self.root_dispatcher
