=======
Facture
=======

--------
Overview
--------

Facture is FAC-tories that create fix-TURE data.  Also, it manu-FACTURE-s data.

Wiktionary says it also means: "The act or manner of making or doing anything,
especially of a literary, musical, or pictorial production."  That's pretty cool.

So why, oh why, would you need such a strange tool?

* "compile"-time checks
* materializes the output into your version-controlled files, unrolling the complexity.  Because this is automated, we can put as much effort into making the generated data comprehensible (and lineage-providing) as possible.  It's also extremely easy to see what the effects of any change you make is, since it's all laid out for you.
* code as configuration (high level of dynamic stuff possible... as long as it runs)
* easy to reason about each scenario in isolation: data partitioning
* plays well with others... strangles manually created fixtures.  Integrates with how you do things, doesn't try to
  take over completely.  Can target files or sections within files.

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
approaches I've taken in the past, in an attempt to always be improving.  It
reads a bit like a blog post.  Yes, it's a bit navel-gazing.  No, I'm not going
to remove it, because I think it's critically important, at least for me.  Feel
free to skip it.  It's at the bottom for a reason.

One thing I've discovered about myself over the past several years is that I
really dislike being confused, particularly when it's entirely avoidable.

I think we owe it to others to put in the effort to polish our creations to
overcome the user's cognitive burden as much as possible.  This article on
research debt really struck a chord with me:
https://distill.pub/2017/research-debt/

No nil checks.  Structural normalization and validation as soon as possible, then confident code after that.

Annotation - build up an evermore complete data structure over time

All on one page - the single document answers all questions

In the example configuration files, boilerplate that explains what the tool is
and how to get it and use it.  Thinking about all the .rc files that I have
come across in the past and wondered "what is this file, what is it for, how do
I use it, etc"

scons says: "Configuration files are Python scripts--use the power of a real programming language to solve build problems."


-------------------
TODO before release
-------------------

* make id being sequential explicit and orderable in arguments
* allow any attribute to be a sequence with a default start integer
* figure out best way to make a Python executable
* target validations
  * not having data generated for them
* check that it supports totally random stuff like $build
* make the reference syntax unambiguous (not '.a.id', but actual reference key + attribute)
* sql output
  * show the table name in the values
  * if multiple records of same type in output, do (1) then (2), etc
* double-check that if you have overlap in generated data that it throws an exception
* break into classes for the different steps
