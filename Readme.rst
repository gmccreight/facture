=======
Facture
=======

--------
Overview
--------

Facture is factories that create fixtures.

TODO: add more text here

* "compile"-time checks
* materializes the output of your configuration
* code as configuration (high level of dynamic stuff possible... as long as it runs)
* easy to reason about each scenario in isolation
* plays well with others.  Integrates with how you do things, doesn't try to take over completely.

----------
How to Use
----------

Create a ``factureconf.py`` file like any of the ones in the examples directory.

Run::

    ./facture.py --conf-dir="the dir with your conf" --output-type=json

-------------------
TODO before release
-------------------

* create a backend that writes the SQL used for inserts
* figure out best way to make a Python executable
