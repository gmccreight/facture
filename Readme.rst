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
* plays well with others.  Integrates with how you do things, doesn't try to
  take over completely.  Can target files or sections within files.

----------
How to Use
----------

Create a ``factureconf.py`` file like any of the ones in the examples directory.

Run::

    ./facture.py --conf-dir="the dir with your conf" --output-type=json

-------------------
How it works
-------------------

Two phases.  First, a validation phase, then a change phase.

Couple of different outputs:

--output-type=json

See the generated data

--output-type=target-injection (the default)

For the targets specified in the factureconf.py conf_targets() method,
inject generated SQL statements.

when in target-injection output mode --empty-targets-ok allows no targets to be
specified, or for some of the targets to not be filled in.

-------------------
TODO before release
-------------------

* create a backend that writes the SQL used for inserts
* figure out best way to make a Python executable
* have tests for targets being sub-par:

  * misconfigured in target files (not paring start with end)
  * not having data generated for them
  * no targets specified in conf file
