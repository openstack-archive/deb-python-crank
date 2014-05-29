Crank
==============

.. image:: https://travis-ci.org/TurboGears/crank.png
    :target: https://travis-ci.org/TurboGears/crank

.. image:: https://coveralls.io/repos/TurboGears/crank/badge.png
    :target: https://coveralls.io/r/TurboGears/crank

.. image:: https://pypip.in/v/crank/badge.png
   :target: https://pypi.python.org/pypi/crank

.. image:: https://pypip.in/d/crank/badge.png
   :target: https://pypi.python.org/pypi/crank

Generalized Object based Dispatch mechanism for use across frameworks.

License
-----------

Crank is licensed under an MIT-style license (see LICENSE.txt).
Other incorporated projects may be licensed under different licenses.
All licenses allow for non-commercial and commercial use.

ChangeLog
--------------

0.7.1
~~~~~~~~~~~~~

- Fix issue that in some cased caused ``_lookup`` to not be called for ``RestDispatcher``
- Speedup permission checks, in some conditions they were performed twice
- Python 3.4 is now officially supported
