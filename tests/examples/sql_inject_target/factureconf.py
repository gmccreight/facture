#############################################################################
# What is this file?
#############################################################################
#
# This is a configuration file for a command-line data creation tool called
# `facture`.
#
# Facture is written in Python.  It can be installed on your system by doing:
#   pip install facturedata
#
# If you have Python set up in a normal way, installing facture will create a
# `facture` binary in your PATH, which you should be able to run simply by
# typing "facture" in the command line.
#
# To be able to use this configuration file with facture, you will either want
# to be in the same directory as this file when you invoke facture, or you will
# need to specify the directory of this configuration file by doing:
#   facture --conf-dir="whatever/directory/this/configuration/file/is/in"
#
#############################################################################
# How to use this file
#############################################################################
#
# This configuration file is written in Python so you can use variables, code,
# add your own helper functions to supplement these functions, etc.  That's not
# a crazy thing to do because facture is a code-generation tool, so you will be
# able to see the completely unrolled result of your changes.  In other words,
# you can be confident that if you make changes here and the output of running
# facture is what you expect, you're good... there are no additional side
# effects you need to be aware of.
#
# One important note is if you're running Python <= 3.5 then the table 'attrs'
# must be defined in an OrderedDict in order to retain attr write order!

import collections

def conf_tables():
    return {
        'actors': {
            'target': 'actors',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 10}}),
                ('job_run_id', {}),
                ('first_name', {'default': None}),
                ('last_name', {'default': None})
            ])
        },
        'films': {
            'target': 'films',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 100}}),
                ('name', {'default': None}),
                ('year', {'default': None}),
            ])
        },
        'roles': {
            'target': 'roles',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 1000}}),
                ('actor_id', {}),
                ('film_id', {})
            ])
        },
    }


def conf_data():
    return [
        {
            'group': 'facture_group_shawshank_redemption',
            'offset': 100,
            'data': [
                ['actors a_mf', {'attrs': {
                    'job_run_id': {'raw': '$build_id'},
                    'first_name': 'Morgan',
                    'last_name': 'Freeman'
                }}],
                ['actors a_tr', {'attrs': {
                    'job_run_id': {'raw': '$build_id'},
                    'first_name': 'Tim',
                    'last_name': 'Robbins'
                }}],
                ['films f', {'attrs': {'name': 'Shawshank Redemption', 'year': '1994'}}],
                ['roles r1', {'refs': {'actor_id': '.a_mf.id', 'film_id': '.f.id'}}],
                ['roles r1', {'refs': {'actor_id': '.a_tr.id', 'film_id': '.f.id'}}]
            ]
        }
    ]


def conf_targets():
    return [
        {
            'name': 'actors',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'actors'
        },
        {
            'name': 'films',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'films'
        },
        {
            'name': 'roles',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'roles'
        }
    ]


