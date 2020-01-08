#############################################################################
# What is this file?
#############################################################################
#
# This file is used to show some of the more advanced features of facture.
# Refer to the `sql_injection_target` example for a more basic use case before
# looking into this
#
#
#############################################################################
# What are the advanced topics?
#############################################################################
# 1. ReferenceObjects:
#       Facture is able to evaluate objects that match the `FactureRefObj`
#       interface. The `StringRefObj` is an example of how you could create
#       a lazily evaluated string that allows you to reference facture anchors
#       in more complex data types.
#

import collections
import re


class StringRefObj:

    ANCHOR_FORMAT = "facture_anchor{{{}}}"

    def __init__(self, string):
        self._anchors = self._regex_anchors(string)
        self.anchor_values = {}
        self.raw_string = string

    @staticmethod
    def _regex_anchors(string):
        reg_anchor = re.compile(r'(?<=facture_anchor\{)[^}]+')
        return re.findall(reg_anchor, string)

    def anchors(self):
        return list(set(self._anchors))

    def bind(self, anchor, value):
        self.anchor_values[anchor] = value

    def eval(self):
        result = self.raw_string
        for anchor in self.anchors():
            result = result.replace(StringRefObj.ANCHOR_FORMAT.format(anchor), str(self.anchor_values[anchor]))
        return result


def conf_tables():
    return {
        'users': {
            'target': 'users',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 10}}),
                ('first_name', {'default': None}),
                ('last_name', {'default': None})
            ])
        },
        'workflows': {
            'target': 'workflows',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 100}}),
                ('name', {}),
                ('query', {}),
                ('created_by', {}),
            ])
        },
        'products': {
            'target': 'products',
            'attrs': collections.OrderedDict([
                ('id', {'seq': {'start': 1000}}),
            ])
        },
    }


def conf_data():
    return [
        {
            'group': 'facture_group_basic_workflow_grouping',
            'offset': 100,
            'data': [
                ['users a_us1', {'attrs': {
                    'first_name': 'Michael',
                    'last_name': 'Scott'
                }}],
                ['users a_us2', {'attrs': {
                    'first_name': 'Dwight',
                    'last_name': 'Schrute'
                }}],
                ['products p_1', {}],
                ['products p_2', {}],
                ['workflows w_1', {
                    'attrs': {'name': 'Tracking Dwight'},
                    'refs': {'created_by': '.a_us1.id'},
                    'ref_objs': {'query': StringRefObj('select * from orders where product_id = facture_anchor{.p_1.id} and user_id = facture_anchor{.a_us2.id}')}}
                 ],
                ['workflows w_2', {
                    'refs': {'created_by': '.a_us2.id'},
                    'attrs': {'query': 'select * from orders where 1=1', 'name': 'Fetch all orders'}
                }]
            ]
        }
    ]


def conf_targets():
    return [
        {
            'name': 'users',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'users'
        },
        {
            'name': 'products',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'products'
        },
        {
            'name': 'workflows',
            'type': 'section_in_file',
            'filename': 'test_output/sql_inject_target/result.sql',
            'section_name': 'workflows'
        }
    ]


