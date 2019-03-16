#############################################################################
# What is this file?
#############################################################################
#
# This is a configuration file for a command-line data creation tool called
# `facture`.
#
# Facture is written in Python.  It can be installed on your system by doing:
#   pip install facture
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


def conf_targets():
    return [
        {
            'name': 'products',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'products'
        }
    ]


def conf_tables():
    return {
        'products': {
            'target': 'products',
            'start_id': 10,
            'attrs': {
                'name': {'default': 'default name'},
            }
        },
    }


def conf_data():
    return [
        {
            'group': 'facture_group_testgroup1',
            'offset': 100,
            'data': [
                ['products p'],
            ]
        },
        {
            'group': 'facture_group_testgroup2',
            'offset': 200,
            'data': [
                [
                    'products p',
                    {'attrs': {'name': 'better name'}}
                ],
            ]
        }
    ]
