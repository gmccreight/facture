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
    return []


def conf_tables():
    default_date = '2018-01-01 00:00:00'
    return {
        'products': {
            'attrs': {
                'id': {'seq': {'start': 21000000000}},
                'classified_code': {'default': '0000001234'},
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        },
        'retailer_products': {
            'attrs': {
                'id': {'seq': {'start': 22000000000}},
                'product_id': {},
                'retailer_id': {},
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        },
        'warehouses': {
            'attrs': {
                'id': {'seq': {'start': 23000000000}},
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        }
    }


def conf_data():
    return [
        {
            'group': 'facture_group_prod1',
            'offset': 10000,
            'data': [
                ['warehouses w'],
                ['products p1'],
                ['products p2'],
                [
                    'retailer_products rp1',
                    {'refs': {'retailer_id': '.w.id', 'product_id': '.p1.id'}}
                ],
                [
                    'retailer_products rp2',
                    {'refs': {'retailer_id': '.w.id', 'product_id': '.p2.id'}}
                ]
            ]
        },
        {
            'group': 'facture_group_prod2',
            'offset': 1000,
            'data': [
                ['warehouses w'],
                ['products p'],
                [
                    'retailer_products rp',
                    {'refs': {'retailer_id': '.w.id', 'product_id': '.p.id'}}
                ]
            ]
        }
    ]
