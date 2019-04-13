=======
Facture
=======

--------
Overview
--------

Facture is FAC-tories that generate partition-isolated fix-TURE data for scenarios.

--------------------------------------------------
How is this different from factories and fixtures?
--------------------------------------------------

Originally this tool was created for generating the test data for a database
that had very high overhead per-insert, so using traditional data factories and
individual transactions with rollback would not work; batching the inserts was
necessary.

Fixtures alone could solve this problem, but it's really hard to enumerate and
manage the joins in a large number of scenarios in fixtures effectively.  The
primary advantage that factories have is their ease of use in testing
individual scenarios without needing to understand other scenarios or manage a
corpus of shared data.  Carefully paritioning inserted data so the data is
unambiguously owned by a scenario can provide the same benefit as factories,
where it becomes easy to understand the data associated with individual
scenarios.

----------
How to Use
----------

Go to the ``tests/examples/sql_inject_target`` directory.  Copy the
``factureconf.py`` to the directory you will be running ``facture`` in.  Look
at the ``facture_json`` target section in the ``original.sql`` file into a file
of your own choosing.  Update the ``conf_targets`` section of your
``factureconf.py`` file to point to the file where you put the ``facture_json``.

Please consider keeping the boilerplate at the top of the configuration file.
It will help people who have never come across facture before to orient
themselves quickly.

Run::

    facture

That section in your target file should now be filled in with some data.
You're off to the races!

-------------------
Additional benefits
-------------------

* "compile"-time factory configuration consistency checks.  Checks for many
  typos, join issues, etc.

* Materializes the output into your version-controlled files, unrolling the
  complexity.  Because the fixtures that we generate are automatically created,
  we can put a lot of effort into making the generated data comprehensible (and
  lineage-providing).  This means we annotate all generated data with the column names, 
  and the scenario name.  It's also extremely easy to see what the effects of
  any change you make is, since it's all laid out for you.

* Code as configuration.  The configuration files are written in Python, so you have
  the full power of the language.

* Easy to reason about each scenario in complete isolation because of data partitioning

* Plays well with others... can be introduced into existing fixtures.  Integrates
  with how you do things, doesn't try to take over completely.  Can target
  files or sections within files.
