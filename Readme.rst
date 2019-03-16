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
* easy to reason about each scenario in isolation: data partitioning
* plays well with others... strangles manually created fixtures.  Integrates with how you do things, doesn't try to
  take over completely.  Can target files or sections within files.

----------
How to Use
----------

Create a ``factureconf.py`` file like any of the ones in the

Go to the ``tests/examples/sql_inject_target`` directory.  Copy the
``factureconf.py`` to the directory you will be running ``facture`` in.  Look
at the ``facture_json`` target section in the ``original.sql`` file into a file
of your own choosing.  Update the ``conf_targets`` section of your
``factureconf.py`` file to point to the file where you put the ``facture_json``.

Run::

    facture

That section in your target file should now be filled in with some data.
You're off to the races!

-------------------
How it works
-------------------

The steps in the process are:

* sequence creation
* data joins
* formatting
* output to targets

=================
Sequence Creation
=================

=================
Data Joins
=================

=================
Formatting
=================

=================
Output to Targets
=================

Unless you specify ``--skip-targets``, facture will verify that you have added
at least a single target, and will output into that target.

--------
Approach
--------

This is my favorite section of every project.  It's where I reflect on the
approach I have taken, how I feel about it, and compare and contrast with
approaches I've taken in the past.

No nil checks.  Structural normalization and validation as soon as possible, then confident code after that.

Annotation - build up an evermore complete data structure over time

All on one page - the single document answers all questions



-------------------
TODO before release
-------------------

* figure out best way to make a Python executable
* target validations
  * not having data generated for them
