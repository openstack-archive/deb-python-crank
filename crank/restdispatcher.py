"""
This module contains the RestDispatcher implementation

Rest controller provides a RESTful dispatch mechanism, and
combines controller decoration for TG-Controller behavior.
"""
from webob.exc import HTTPMethodNotAllowed
from dispatcher import get_argspec
from objectdispatcher import ObjectDispatcher

class RestDispatcher(ObjectDispatcher):
    """Defines a restful interface for a set of HTTP verbs.
    Please see RestController for a rundown of the controller
    methods used.
    """

    def _find_first_exposed(self, controller, methods):
        for method in methods:
            if self._is_exposed(controller, method):
                return getattr(controller, method)

    def _setup_wsgiorg_routing_args(self, url_path, remainder, params):
        pass
        #request.environ['wsgiorg.routing_args'] = (tuple(remainder), params)

    def _handle_put_or_post(self, method, state, remainder):
        current_controller = state.controller
        if remainder:
            current_path = remainder[0]
            if self._is_exposed(current_controller, current_path):
                state.add_method(getattr(current_controller, current_path), remainder[1:])
                return state

            if self._is_controller(current_controller, current_path):
                current_controller = getattr(current_controller, current_path)
                return self._dispatch_controller(current_path, current_controller, state, remainder[1:])

        method_name = method
        method = self._find_first_exposed(current_controller, [method,])
        if method and self._method_matches_args(method, state, remainder):
            state.add_method(method, remainder)
            return state

        return self._dispatch_first_found_default_or_lookup(state, remainder)

    def _handle_delete(self, method, state, remainder):
        current_controller = state.controller
        method_name = method
        method = self._find_first_exposed(current_controller, ('post_delete', 'delete'))

        if method and self._method_matches_args(method, state, remainder):
            state.add_method(method, remainder)
            return state

        #you may not send a delete request to a non-delete function
        if remainder and self._is_exposed(current_controller, remainder[0]):
            raise HTTPMethodNotAllowed

        # there might be a sub-controller with a delete method, let's go see
        if remainder:
            sub_controller = getattr(current_controller, remainder[0], None)
            if sub_controller:
                remainder = remainder[1:]
                state.current_controller = sub_controller
                state.url_path = '/'.join(remainder)
                r = self._dispatch_controller(state.url_path, sub_controller, state, remainder)
                if r:
                    return r
        return self._dispatch_first_found_default_or_lookup(state, remainder)

    def _check_for_sub_controllers(self, state, remainder):
        current_controller = state.controller
        method = None
        for find in ('get_one', 'get'):
            if hasattr(current_controller, find):
                method = find
                break
        if method is None:
            return
        args = get_argspec(getattr(current_controller, method))
        fixed_args = args[0][1:]
        fixed_arg_length = len(fixed_args)
        var_args = args[1]
        if var_args:
            for i, item in enumerate(remainder):
                if hasattr(current_controller, item) and self._is_controller(current_controller, item):
                    current_controller = getattr(current_controller, item)
                    state.add_routing_args(item, remainder[:i], fixed_args, var_args)
                    return self._dispatch_controller(item, current_controller, state, remainder[i+1:])
        elif fixed_arg_length< len(remainder) and hasattr(current_controller, remainder[fixed_arg_length]):
            item = remainder[fixed_arg_length]
            if hasattr(current_controller, item):
                if self._is_controller(current_controller, item):
                    state.add_routing_args(item, remainder, fixed_args, var_args)
                    return self._dispatch_controller(item, getattr(current_controller, item), state, remainder[fixed_arg_length+1:])

    def _handle_delete_edit_or_new(self, state, remainder):
        method_name = remainder[-1]
        if method_name not in ('new', 'edit', 'delete'):
            return
        if method_name == 'delete':
            method_name = 'get_delete'

        current_controller = state.controller

        if self._is_exposed(current_controller, method_name):
            method = getattr(current_controller, method_name)
            new_remainder = remainder[:-1]
            if method and self._method_matches_args(method, state, new_remainder):
                state.add_method(method, new_remainder)
                return state

    def _handle_custom_get(self, state, remainder):
        method_name = remainder[-1]
        if method_name not in getattr(self, '_custom_actions', []):
            return

        current_controller = state.controller

        if (self._is_exposed(current_controller, method_name) or
           self._is_exposed(current_controller, 'get_%s' % method_name)):
            method = self._find_first_exposed(current_controller, ('get_%s' % method_name, method_name))
            new_remainder = remainder[:-1]
            if method and self._method_matches_args(method, state, new_remainder):
                state.add_method(method, new_remainder)
                return state

    def _handle_custom_method(self, method, state, remainder):
        current_controller = state.controller
        method_name = method
        method = self._find_first_exposed(current_controller, ('post_%s' % method_name, method_name))

        if method and self._method_matches_args(method, state, remainder):
            state.add_method(method, remainder)
            return state

        #you may not send a delete request to a non-delete function
        if remainder and self._is_exposed(current_controller, remainder[0]):
            raise HTTPMethodNotAllowed

        # there might be a sub-controller with a delete method, let's go see
        if remainder:
            sub_controller = getattr(current_controller, remainder[0], None)
            if sub_controller:
                remainder = remainder[1:]
                state.current_controller = sub_controller
                state.url_path = '/'.join(remainder)
                r = self._dispatch_controller(state.url_path, sub_controller, state, remainder)
                if r:
                    return r
        return self._dispatch_first_found_default_or_lookup(state, remainder)

    def _handle_get(self, method, state, remainder):
        current_controller = state.controller
        if not remainder:
            method = self._find_first_exposed(current_controller, ('get_all', 'get'))
            if method:
                state.add_method(method, remainder)
                return state
            if self._is_exposed(current_controller, 'get_one'):
                method = current_controller.get_one
                if method and self._method_matches_args(method, state, remainder):
                    state.add_method(method, remainder)
                    return state
            return self._dispatch_first_found_default_or_lookup(state, remainder)

        #test for "delete", "edit" or "new"
        r = self._handle_delete_edit_or_new(state, remainder)
        if r:
            return r

        #test for custom REST-like attribute
        r = self._handle_custom_get(state, remainder)
        if r:
            return r

        current_path = remainder[0]
        if self._is_exposed(current_controller, current_path):
            state.add_method(getattr(current_controller, current_path), remainder[1:])
            return state

        if self._is_controller(current_controller, current_path):
            current_controller = getattr(current_controller, current_path)
            return self._dispatch_controller(current_path, current_controller, state, remainder[1:])

        if self._is_exposed(current_controller, 'get_one') or self._is_exposed(current_controller,  'get'):

            if self._is_exposed(current_controller, 'get_one'):
                method = current_controller.get_one
            else:
                method = current_controller.get

            if method and self._method_matches_args(method, state, remainder):
                state.add_method(method, remainder)
                return state

        return self._dispatch_first_found_default_or_lookup(state, remainder)

    _handler_lookup = {
        'put':_handle_put_or_post,
        'post':_handle_put_or_post,
        'delete':_handle_delete,
        'get':_handle_get,
        }

    def _dispatch(self, state, remainder):
        """returns: populated DispachState object
        """

        log.debug('Entering dispatch for remainder: %s in controller %s'%(remainder, self))
        if not hasattr(state, 'http_method'):
            method = state.request.method.lower()
            params = state.params

            #conventional hack for handling methods which are not supported by most browsers
            request_method = params.get('_method', None)
            if request_method:
                request_method = request_method.lower()
                #make certain that DELETE and PUT requests are not sent with GET
                if method == 'get' and request_method == 'put':
                    raise HTTPMethodNotAllowed
                if method == 'get' and request_method == 'delete':
                    raise HTTPMethodNotAllowed
                method = request_method
            state.http_method = method

        r = self._check_for_sub_controllers(state, remainder)
        if r:
            return r

        if state.http_method in self._handler_lookup.keys():
            r = self._handler_lookup[state.http_method](self, state.http_method, state, remainder)
        else:
            r = self._handle_custom_method(state.http_method, state, remainder)
        return r
