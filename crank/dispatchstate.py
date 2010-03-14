"""
This module implements the :class:`DispatchState` class
"""
from util import odict, Path

class DispatchState(object):
    """
    This class keeps around all the pertainent info for the state
    of the dispatch as it traverses through the tree.  This allows
    us to attach things like routing args and to keep track of the
    path the controller takes along the system.
    """
    path = Path()

    def __init__(self, request, dispatcher=None, params=None):
        self.request = request
        self.path = request.path_info
        self.path = self.path[1:]

        if params is not None:
            self.params = params
        else:
            self.params = request.params

        self.controller_path = odict()
        self.routing_args = {}
        self.method = None
        self.remainder = None
        self.dispatcher = dispatcher
        self.add_controller('/', dispatcher)

    def add_controller(self, location, controller):
        """Add a controller object to the stack"""
        self.controller_path[location] = controller

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

    @property
    def controller(self):
        """returns the current controller"""
        return self.controller_path.getitem(-1)
