"""
"""
import web.core
from restdispatcher import RestDispatcher
from dispatcher import DispatchState
import mimetypes

class RestController(RestDispatcher):

    def __call__(self, *args, **kw):
        verb = kw.get('_method', None)

        request = web.core.request
        url_path = '/'.join(args)
        state = DispatchState(url_path, kw)
        state.request = request
        state.add_controller('/', self)
        state.dispatcher = self
        state =  state.controller._dispatch(state, args)

        verb = kw.pop('_verb', request.method).lower()

        # attach the request to the controller for use without the
        # cost of a SOP.
        # also, save the dispatch state
        try:
            state.controller.request
            state.controller.dispatch_state
        except AttributeError:
            state.controller.request = request
            state.controller.dispatch_state = state

        return state.method(*state.remainder, **kw)

    def __before__(self, *args, **kw):
        return (args, kw)

    def __after__(self, result, *args, **kw):
        """The __after__ method can modify the value returned by the final method call."""
        return result

    index = __call__
    __default__ = __call__
