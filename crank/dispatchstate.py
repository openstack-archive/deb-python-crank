"""
This module implements the :class:`DispatchState` class
"""
from util import Path

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
    """

    def __init__(self, request, dispatcher=None, params=None, path_info=None, ignore_parameters=None):
        self.request = request

        path = path_info
        if path is None:
            path = request.path_info[1:]

            path = path.split('/')
        elif isinstance(path, basestring):
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

        self.extension = None

        #rob the extension
        if len(path) > 0 and '.' in path[-1]:
            end = path[-1]
            end = end.split('.')
            self.extension = end[-1]
            path[-1] = '.'.join(end[:-1])
                

        self.path = path
            

        if params is not None:
            self.params = params
        else:
            self.params = request.params

        #remove the ignore params from self.params
        if ignore_parameters:
            remove_params = ignore_parameters
            for param in remove_params:
                if param in self.params:
                    del self.params[param]

        self.controller = None
        self.controller_path = []
        self.routing_args = {}
        self.method = None
        self.remainder = None
        self.dispatcher = dispatcher
        self.add_controller('/', dispatcher)
        self._notfound_stack = []

    def add_controller(self, location, controller):
        """Add a controller object to the stack"""
        self.controller = controller
        self.controller_path.append((location, controller))

    def add_method(self, method, remainder):
        """Add the final method that will be called in the _call method"""
        self.method = method
        self.remainder = remainder

    def add_routing_args(self, current_path, remainder, fixed_args, var_args):
        """
        Add the "intermediate" routing args for a given controller mounted
        at the current_path
        """
        i = 0
        for i, arg in enumerate(fixed_args):
            if i >= len(remainder):
                break
            self.routing_args[arg] = remainder[i]
        remainder = remainder[i:]
        if var_args and remainder:
            self.routing_args[current_path] = remainder
