#!/usr/bin/env python3

import argparse
import copy
import json
import logging
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-v', action="count", default=0)
parser.add_argument('--doctest', action="store_true")
parser.add_argument('--conf-dir', type=str)
parser.add_argument('--output-type', type=str, choices=['json', 'sql'])
args = parser.parse_args()

if args.v >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.v >= 1:
    logging.basicConfig(level=logging.INFO)


class ConfError(Exception):
    pass


def debug(m):
    logging.debug(m)


if not args.doctest:
    if args.conf_dir:
        if not os.path.isdir(args.conf_dir):
            raise ConfError("conf-dir {} does not exist".format(args.conf_dir))
        sys.path.insert(0, args.conf_dir)
    else:
        if not os.path.isfile("factureconf.py"):
            raise ConfError("Either put a factureconf.py file in this directory or set --conf-dir")

    import factureconf # noqa


def run():
    id_seqs = {}
    config = factureconf.conf_tables()

    d = factureconf.conf_data()

    d = normalize_structure(d)

    consistency_checks_or_immediately_die(d)

    d = enhance_with_generated_data(d, id_seqs, config)

    d = add_table_defaults(d, config)

    d = combine_all_into_result(d)

    if args.output_type and args.output_type == 'json':
        print(json.dumps(d, indent=4, sort_keys=True, default=str))

#############################################################################


def normalize_structure(data):
    data = normalize_structure_copy_raw(data)

    data = normalize_structure_ensure_dictionaries(data)
    return data


def normalize_structure_copy_raw(data):
    """We get a certain easy-to-input structure.  Keep in in raw.

    >>> d = [{'data': [['calls c', {'attrs': {'f': 'b'}}]]}]
    >>> normalize_structure_copy_raw(d)
    [{'data': [{'raw': {'tablestr': 'calls c', 'attrs': {'f': 'b'}}}]}]
    """

    result = copy.deepcopy(data)

    for x in result:
        new_data = []
        for y in x['data']:
            if len(y) == 1:
                y.append({})
            raw = {'tablestr': y[0]}
            raw.update({'attrs': y[1].get('attrs')})
            new_data.append({'raw': raw})
        x['data'] = new_data

    return result


def normalize_structure_ensure_dictionaries(data):
    """This adds dictionaries to each of the 'data' list items.

    >>> d = [{'data': [{'raw': {'tablestr': 't x', 'attrs': {'f': 'b'}}}]}]
    >>> res = normalize_structure_ensure_dictionaries(d)

    >>> res[0]['data'][0]['raw'] == d[0]['data'][0]['raw'] # no change
    True
    >>> res[0]['data'][0]['table']
    't'
    >>> res[0]['data'][0]['alias']
    'x'

    >>> d = [{'data': [{'raw': {'tablestr': 't', 'attrs': {'f': 'b'}}}]}]
    >>> normalize_structure_ensure_dictionaries(d)
    Traceback (most recent call last):
    ConfError: in "data", "t" needs an alias
    """

    result = copy.deepcopy(data)

    for x in result:
        for y in x['data']:
            raw = y['raw']
            table_and_alias = raw['tablestr'].split(' ')
            if len(table_and_alias) == 2:
                y.update({'table': table_and_alias[0]})
                y.update({'alias': table_and_alias[1]})
            else:
                raise ConfError('in "data", "{}" needs an alias'.format(
                    raw['tablestr']
                ))

    return result


#############################################################################


def consistency_checks_or_immediately_die(data):
    consistency_check_offset(data)
    consistency_check_no_same_aliases(data)
    consistency_check_no_same_groups(data)


def consistency_check_offset(data):
    """Check whether the offsets overlap

    >>> consistency_check_offset([{'offset': 100}, {'offset': 200}])
    True

    >>> consistency_check_offset([{'offset': 100}, {'offset': 100}])
    Traceback (most recent call last):
    ConfError: These offsets are duplicated: {100}
    """

    offsets = [i['offset'] for i in data]
    dups = set([x for x in offsets if offsets.count(x) > 1])
    if len(dups) == 0:
        return True
    else:
        raise ConfError('These offsets are duplicated: {}'.format(dups))


def consistency_check_no_same_aliases(data):
    # TODO
    return True


def consistency_check_no_same_groups(data):
    # TODO
    return True


#############################################################################


def enhance_with_generated_data(data, id_seqs, config):
    data = add_generated_key_and_dict(data)
    data = enhance_with_generated_data_ids(data, id_seqs, config)

    data = enhance_with_referenced_foreign_ids(data)

    return data


def add_generated_key_and_dict(data):
    """This adds the 'generated' key and dictionary

    >>> d = [{'data': [{'table': 'calls'}]}]
    >>> add_generated_key_and_dict(d)
    [{'data': [{'table': 'calls', 'generated': {'id': None}}]}]
    """

    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            y['generated'] = {'id': None}
    return result


def enhance_with_generated_data_ids(data, id_seqs, config):
    """This enhances the data with generated ids.

    >>> id_seqs = {}
    >>> config = {'calls': {'start_id': 300}}
    >>> d = [{'offset': 3, 'data': \
            [{'table': 'calls', 'generated': {'id': None}}]}]
    >>> enhance_with_generated_data_ids(d, id_seqs, config)
    [{'offset': 3, 'data': [{'table': 'calls', 'generated': {'id': 303}}]}]
    """

    result = copy.deepcopy(data)
    for x in result:
        offset = x['offset']
        for y in x['data']:
            num, id_seqs = id_for(y['table'], offset, id_seqs, config)
            y['generated']['id'] = num

    return result


def id_for(table, offset, id_seqs, config):
    """This generates sequence numbers for each offset
    """

    if id_seqs == {}:
        for key in config:
            id_seqs[key] = {}

    if id_seqs[table].get(offset) is None:
        id_seqs[table][offset] = config[table]['start_id'] + offset

    result = id_seqs[table][offset]
    id_seqs[table][offset] += 1

    return result, id_seqs


def enhance_with_referenced_foreign_ids(data):
    """This enhances the data by adding the foreign keys to the aliases
    """
    result = copy.deepcopy(data)
    for x in result:
        group_data = x['data']
        for y in group_data:
            y['referenced'] = {}
            raw = y['raw']
            attrs = raw.get('attrs')
            if attrs:
                for k, v in attrs.items():
                    if v[0] == '.':
                        v = point_to_alias(
                                v, x['group'], group_data
                        )
                    y['referenced'][k] = v

    return result


def point_to_alias(refstr, group_name, group_data):
    """ Given a refstr, get attribute value in target.

    >>> d = [{'alias': 'p', 'generated': {'id': 231}}]

    >>> point_to_alias('.p.id', 'z', d)
    231

    >>> point_to_alias('.id', 'z', d)
    Traceback (most recent call last):
    ConfError: refstr ".id" incorrectly formatted in group "z"

    >>> point_to_alias('.x.id', 'z', d)
    Traceback (most recent call last):
    ConfError: refstr: alias "x" does not exist in group "z"

    >>> point_to_alias('.p.y', 'z', d)
    Traceback (most recent call last):
    ConfError: key "y" missing for alias "p" in group "z"
    """

    def err(m):
        raise ConfError(m)

    alias_and_key = refstr.split('.')
    if len(alias_and_key) != 3:
        err('refstr "{}" incorrectly formatted in group "{}"'.format(
            refstr, group_name
        ))

    alias = alias_and_key[1]
    key = alias_and_key[2]

    record = None
    for x in group_data:
        if x['alias'] == alias:
            record = x

    if record is None:
        err('refstr: alias "{}" does not exist in group "{}"'.format(
            alias, group_name
        ))

    if len(alias_and_key) != 3:
        err('refstr "{}" incorrectly formatted in group "{}"'.format(
            refstr, group_name
        ))

    new_value = record['generated'].get(key)
    if new_value is None:
        err('key "{}" missing for alias "{}" in group "{}"'.format(
            key, alias, group_name
        ))

    return new_value


#############################################################################


def add_table_defaults(data, my_conf_tables):
    """ Update the data with lower-ranking default table data

    >>> d = [{'data': [{'table': 'calls'}]}]
    >>> c = {'calls': {'attrs': {'foo': {'default': 'bar'}}}}

    >>> add_table_defaults(d, c)
    [{'data': [{'table': 'calls', 'defaults': {'foo': 'bar'}}]}]


    >>> d = [{'data': [{'table': 'whoops'}]}]
    >>> c = {'calls': {'attrs': {'foo': {'default': 'bar'}}}}

    >>> add_table_defaults(d, c)
    Traceback (most recent call last):
    ConfError: table "whoops" has no default attrs conf
    """

    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            y['defaults'] = {}
            table = y['table']
            table_conf = my_conf_tables.get(table)
            if table_conf is None:
                raise ConfError(
                    'table "{}" has no default attrs conf'.format(table)
                )
            attrs = table_conf['attrs']
            for i in attrs.items():
                default = i[1].get('default')
                if default:
                    y['defaults'].update({i[0]: default})
    return result


#############################################################################

def careful_merge_dicts(d1, d2):
    d1 = copy.deepcopy(d1)
    d2 = copy.deepcopy(d2)
    if any(d1[k] != d2[k] for k in d1.keys() & d2):
        raise ConfError(
            'There were overlapping keys in merging dictionaries: {}, {}'
        ).format(d1, d2)
    else:
        d1.update(d2)
        return d1


def combine_all_into_result(data):
    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            z = y['defaults']
            z.update(y['referenced'])
            z = careful_merge_dicts(z, y['generated'])
            y['combined'] = z
    return result


def formatted_single_record_lines(attrs):
    """ Format the record data

    >>> attrs = {\
        "id": 21000010000,\
        "classified_code": "0000001234",\
        "created_at": "2018-01-01 00:00:00",\
        "updated_at": "2018-01-01 00:00:00"\
    }
    >>> formatted_single_record_lines(attrs)[0]
    '21000010000,           -- id'
    >>> formatted_single_record_lines(attrs)[1]
    "'0000001234',          -- classified_code"
    >>> formatted_single_record_lines(attrs)[2]
    "'2018-01-01 00:00:00', -- created_at"
    >>> formatted_single_record_lines(attrs)[3]
    "'2018-01-01 00:00:00'  -- updated_at"
    """

    max_width = max([len(repr(i)) for i in attrs.values()])

    results = []
    for i in enumerate(attrs.items()):
        index = i[0]
        value = i[1][1]
        key = i[1][0]
        value_str = "{}".format(repr(value))
        comma_or_space = ' '
        if index < len(attrs.items()) - 1:
            comma_or_space = ','
        num_spaces_to_add = max_width - len(value_str)
        space_after = ' ' * num_spaces_to_add
        results += [value_str + comma_or_space + space_after + ' -- ' + key]
    return results


def parse_facture_json_line(line, filename, linenum):
    """ Parse the JSON in the facture_json line

    >>> l = 'just a normal line'
    >>> parse_facture_json_line(l, './foo', 12)

    >>> l = '-- facture_json: {"target_name": "products", "position": "end"}'
    >>> parse_facture_json_line(l, './foo', 12)['target_name']
    'products'

    >>> l = '-- facture_json: {whoops": "end"}'
    >>> parse_facture_json_line(l, './foo.sql', 34)
    Traceback (most recent call last):
    ConfError: facture_json on line 34 in './foo.sql' is not valid JSON
    """

    m = re.match(r'.*facture_json: (.*)', line)
    if m:
        json_text = m[1]
        result = None
        try:
            result = json.loads(json_text)
        except json.decoder.JSONDecodeError as e:
            raise ConfError(
                "facture_json on line {} in '{}' is not valid JSON".format(linenum, filename)
            ) from e
        return result
    else:
        return None


#############################################################################


def config_for(table):
    return factureconf.conf_tables()[table]


id_seqs = None

if __name__ == '__main__':
    if args.doctest:
        import doctest
        doctest.testmod()
    else:
        run()
