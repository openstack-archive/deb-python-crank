"""
This is the main dispatcher module.

Dispatch works as follows:
Start at the RootController, the root controller must
have a _dispatch function, which defines how we move
from object to object in the system.
Continue following the dispatch mechanism for a given
controller until you reach another controller with a
_dispatch method defined.  Use the new _dispatch
method until anther controller with _dispatch defined
or until the url has been traversed to entirety.

This module also contains the standard ObjectDispatch
class which provides the ordinary TurboGears mechanism.

"""

class odict(dict):

    def __init__(self, *args, **kw):
        self._ordering = []
        dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        self._ordering.append(key)
        dict.__setitem__(self, key, value)

    def keys(self):
        return self._ordering

    def clear(self):
        self._ordering = []
        dict.clear(self)

    def getitem(self, n):
        return self[self._ordering[n]]

#    def __slice__(self, a, b, n):
#        return self.values()[a:b:n]

    def iteritems(self):
        for item in self._ordering:
            yield item, self[item]

    def items(self):
        return [i for i in self.iteritems()]

    def itervalues(self):
        for item in self._ordering:
            yield self[item]

    def values(self):
        return [i for i in self.itervalues()]

#xxx: fixme
#    def __del__(self, key, x):
#        self._ordering.remove(key)
#        dict.__delete__(self, key)

    def pop(self):
        item = self._ordering[-1]
        del self[item]
        self._ordering.remove(item)

    def __str__(self):
        return str(self.items())

from inspect import getargspec

_cached_argspecs = {}
def get_argspec(func):
    try:
        im_func = func.im_func
    except AttributeError:
        im_func = func
    try:
        argspec = _cached_argspecs[im_func]
    except KeyError:
        argspec = _cached_argspecs[im_func] = getargspec(func)
    return argspec

def get_params_with_argspec(func, params, remainder):
    params = params.copy()
    argspec = get_argspec(func)
    argvars = argspec[0][1:]
    if argvars and enumerate(remainder):
        for i, var in enumerate(argvars):
            if i >= len(remainder):
                break
            params[var] = remainder[i]
    return params

def remove_argspec_params_from_params(func, params, remainder):
    """Remove parameters from the argument list that are
       not named parameters
       Returns: params, remainder"""

    # figure out which of the vars in the argspec are required
    argspec = get_argspec(func)
    argvars = argspec[0][1:]

    # if there are no required variables, or the remainder is none, we
    # have nothing to do
    if not argvars or not remainder:
        return params, remainder

    # this is a work around for a crappy api choice in getargspec
    argvals = argspec[3]
    if argvals is None:
        argvals = []

    required_vars = argvars
    optional_vars = []
    if argvals:
        required_vars = argvars[:-len(argvals)]
        optional_vars = argvars[-len(argvals):]

    # make a copy of the params so that we don't modify the existing one
    params=params.copy()

    # replace the existing required variables with the values that come in
    # from params these could be the parameters that come off of validation.
    remainder = list(remainder)
    for i, var in enumerate(required_vars):
        if i < len(remainder):
            remainder[i] = params[var]
        elif params.get(var):
            remainder.append(params[var])
        if var in params:
            del params[var]

    #remove the optional positional variables (remainder) from the named parameters
    # until we run out of remainder, that is, avoid creating duplicate parameters
    for i,(original,var) in enumerate(zip(remainder[len(required_vars):],optional_vars)):
        if var in params:
            remainder[ len(required_vars)+i ] = params[var]
            del params[var]

    return params, tuple(remainder)


def method_matches_args(method, state, remainder):
    """
    This method matches the params from the request along with the remainder to the
    method's function signiture.  If the two jive, it returns true.

    It is very likely that this method would go into ObjectDispatch in the future.
    """
    argspec = get_argspec(method)
    argvars = argspec[0][1:]
    argvals = argspec[3]

    required_vars = argvars
    if argvals:
        required_vars = argvars[:-len(argvals)]
    else:
        argvals = []

    #remove the appropriate remainder quotient
    if len(remainder)<len(required_vars):
        #pull the first few off with the remainder
        required_vars = required_vars[len(remainder):]
    else:
        #there is more of a remainder than there is non optional vars
        required_vars = []

    #remove vars found in the params list
    params = state.params
    for var in required_vars[:]:
        if var in params:
            required_vars.pop(0)
        else:
            break;

    var_in_params = 0
    for var in argvars:
        if var in params:
            var_in_params+=1

    #make sure all of the non-optional-vars are there
    if not required_vars:
        var_args = argspec[0][1:]
        #there are more args in the remainder than are available in the argspec
        if len(var_args)<len(remainder) and not argspec[1]:
            return False
        defaults = argspec[3] or []
        var_args = var_args[len(remainder):-len(defaults)]
        for arg in var_args:
            if arg not in state.params:
                return False
        return True
    return False
