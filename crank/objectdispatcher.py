"""
This is the main dispatcher module.

Dispatch works as follows:
Start at the Originating dispatcher, which must
have a _dispatch function, which defines how we move
from dispatch object to dispatch object in the system.
Continue following the dispatch mechanism for a given
controller until you reach another controller with a
_dispatch method defined.  Use the new _dispatch
method until another controller with _dispatch defined
or until the url has been traversed to entirety.

This module also contains the standard ObjectDispatch
class which provides the ordinary TurboGears mechanism.

"""

from util import get_argspec, method_matches_args
from dispatcher import Dispatcher
from webob.exc import HTTPNotFound
from inspect import ismethod

class ObjectDispatcher(Dispatcher):
    """
    Object dispatch (also "object publishing") means that each portion of the
    URL becomes a lookup on an object.  The next part of the URL applies to the
    next object, until you run out of URL.  Processing starts on a "Root"
    object.

    Thus, /foo/bar/baz become URL portion "foo", "bar", and "baz".  The
    dispatch looks for the "foo" attribute on the Root URL, which returns
    another object.  The "bar" attribute is looked for on the new object, which
    returns another object.  The "baz" attribute is similarly looked for on
    this object.

    Dispatch does not have to be directly on attribute lookup, objects can also
    have other methods to explain how to dispatch from them.  The search ends
    when a decorated controller method is found.

    The rules work as follows:

    1) If the current object under consideration is a decorated controller
       method, the search is ended.

    2) If the current object under consideration has a "default" method, keep a
       record of that method.  If we fail in our search, and the most recent
       method recorded is a "default" method, then the search is ended with
       that method returned.

    3) If the current object under consideration has a "lookup" method, keep a
       record of that method.  If we fail in our search, and the most recent
       method recorded is a "lookup" method, then execute the "lookup" method,
       and start the search again on the return value of that method.

    4) If the URL portion exists as an attribute on the object in question,
       start searching again on that attribute.

    5) If we fail our search, try the most recent recorded methods as per 2 and
       3.
    """

    #Change to True to allow extra params to pass thru the dispatch
    _use_lax_params = False

    def _is_exposed(self, controller, name):
        """Override this function to define how a controller method is
        determined to be exposed.

        :Arguments:
          controller - controller with methods that may or may not be exposed.
          name - name of the method that is tested.

        :Returns:
           True or None
        """
        return ismethod(getattr(controller, name, False))

    def _dispatch_controller(self, current_path, controller, state, remainder):
        """
           Essentially, this method defines what to do when we move to the next
           layer in the url chain, if a new controller is needed.
           If the new controller has a _dispatch method, dispatch proceeds to
           the new controller's mechanism.

           Also, this is the place where the controller is checked for
           controller-level security.
        """
        if hasattr(controller, '_dispatch'):
            obj = getattr(controller, 'im_self', controller)

            security_check = getattr(obj, '_check_security', None)
            if security_check:
                security_check()
            state.add_controller(current_path, controller)
            state.dispatcher = controller
            return controller._dispatch(state, remainder)
        state.add_controller(current_path, controller)
        return self._dispatch(state, remainder)

    def _dispatch_first_found_default_or_lookup(self, state, remainder):
        """
        When the dispatch has reached the end of the tree but not found an
        applicable method, so therefore we head back up the branches of the
        tree until we found a method which matches with a default or lookup method.
        """

        orig_url_path = state.url_path
        if len(remainder):
            state.url_path = state.url_path[:-len(remainder)]
        for i in xrange(len(state.controller_path)):
            controller = state.controller
            if self._is_exposed(controller, '_default'):
                state.add_method(controller._default, remainder)
                state.dispatcher = self
                return state
            if self._is_exposed(controller, '_lookup'):
                controller, remainder = controller._lookup(*remainder)
                last_tried_abstraction = getattr(self, '_last_tried_abstraction', None)
                if type(last_tried_abstraction) != type(controller):
                    self._last_tried_abstraction = controller
                    return self._dispatch_controller('_lookup', controller, state, remainder)
            if self._is_exposed(controller, 'index') and\
               method_matches_args(controller.index, state.params, remainder, self._use_lax_params):
                state.add_method(controller.index, remainder)
                state.dispatcher = self
                return state
            state.controller_path.pop()
            if len(state.url_path):
                remainder = list(remainder)
                remainder.insert(0, state.url_path[-1])
                state.url_path.pop()
        raise HTTPNotFound

    def _dispatch(self, state, remainder=None):
        """
        This method defines how the object dispatch mechanism works, including
        checking for security along the way.
        """
        if state.dispatcher is None:
            state.dispatcher = self
            state.add_controller('/', self)
        if remainder is None:
            remainder = state.url_path
        current_controller = state.controller

        if hasattr(current_controller, '_check_security'):
            current_controller._check_security()
        #we are plumb out of path, check for index
        if not remainder:
            if self._is_exposed(current_controller, 'index') and \
               method_matches_args(current_controller.index, state.params, remainder, self._use_lax_params):
                state.add_method(current_controller.index, remainder)
                return state
            #if there is no index, head up the tree
            #to see if there is a default or lookup method we can use
            return self._dispatch_first_found_default_or_lookup(state, remainder)

        current_path = remainder[0]

        #an exposed method matching the path is found
        if self._is_exposed(current_controller, current_path):
            #check to see if the argspec jives
            controller = getattr(current_controller, current_path)
            if method_matches_args(controller, state.params, remainder[1:], self._use_lax_params):
                state.add_method(controller, remainder[1:])
                return state

        #another controller is found
        if hasattr(current_controller, current_path):
            current_controller = getattr(current_controller, current_path)
            return self._dispatch_controller(
                current_path, current_controller, state, remainder[1:])

        #dispatch not found
        return self._dispatch_first_found_default_or_lookup(state, remainder)

    def _setup_wsgiorg_routing_args(self, url_path, remainder, params):
        """
        This is expected to be overridden by any subclass that wants to set
        the routing_args (RestController). Do not delete.
        """
