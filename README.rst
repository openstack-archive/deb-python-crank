Crank
==============

.. image:: https://travis-ci.org/TurboGears/crank.png
    :target: https://travis-ci.org/TurboGears/crank

.. image:: https://coveralls.io/repos/TurboGears/crank/badge.png
    :target: https://coveralls.io/r/TurboGears/crank

Generalized Object based Dispatch mechanism for use across frameworks.

License
-----------

Crank is licensed under an MIT-style license (see LICENSE.txt).
Other incorporated projects may be licensed under different licenses.
All licenses allow for non-commercial and commercial use.

ChangeLog
--------------

0.8.1
~~~~~

- Improved support for decorated functions that provide ``__wrapped__``.

0.8.0
~~~~~

- New DispatchState api ( See http://turbogears.readthedocs.io/en/tg2.3.8/reference/classes.html#crank.dispatchstate.DispatchState )
- Support for flattening function arguments through ``crank.utils.flatten_arguments``
- ``crank.utils.remove_argspec_params_from_params`` deprecated

0.7.3
~~~~~~~~~~~~~

- Add initial support for Python 3.5

0.7.2
~~~~~~~~~~~~~

- Fix issue with parameters with ``None`` value when preparing positional arguments for dispatch.

0.7.1
~~~~~~~~~~~~~

- Fix issue that in some cased caused ``_lookup`` to not be called for ``RestDispatcher``
- Speedup permission checks, in some conditions they were performed twice
- Python 3.4 is now officially supported
