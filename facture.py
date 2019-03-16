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
parser.add_argument('--skip-targets', action="store_true")
args = parser.parse_args()

if args.v >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.v >= 1:
    logging.basicConfig(level=logging.INFO)


class ConfError(Exception):
    pass


def debug(m):
    logging.debug(m)


def se(m):
    sys.stderr.write(str(m))


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
    conf_tables = factureconf.conf_tables()

    d = factureconf.conf_data()

    d = normalize_structure(d)

    consistency_checks_or_immediately_die(d)

    d = enhance_with_generated_data(d, id_seqs, conf_tables)

    d = add_table_defaults(d, conf_tables)

    d = combine_all_into_result(d)

    d = add_sql_output(d)

    targets = factureconf.conf_targets()
    targets = annotate_targets_with_positional_data_from_file(targets)

    d = add_target_info(d, conf_tables, targets)

    if args.output_type and args.output_type == 'json':
        print(json.dumps(d, indent=4, sort_keys=True, default=str))

    if not args.skip_targets:

        if len(targets) < 1:
            raise ConfError(
                "You have no targets specified in the conf_targets function."
                " Use --skip-targets if that is intentional."
            )

        for target in targets:
            filename = target['filename']
            with open(filename, 'r') as f:

                data = get_facture_json_data_from_file(filename, f.read())

                start_line = None
                end_line = None

                for datum in data:
                    opts = datum['data']
                    if opts['target_name'] == target['name'] and opts['position'] == 'start':
                        start_line = datum['linenum']

                for datum in data:
                    if opts['target_name'] == target['name'] and opts['position'] == 'end':
                        end_line = datum['linenum']

                if not start_line:
                    raise ConfError(
                        "could not find a start for target {}".format(target['name'])
                    )

                if not end_line:
                    raise ConfError(
                        "could not find an end for target {}".format(target['name'])
                    )

                f.seek(0)

                result = []
                for index, line in enumerate(f):
                    linenum = index + 1
                    if linenum <= start_line:
                        result.append(line)
                    if linenum == start_line + 1:
                        result.append("hello there\n")
                    if linenum >= end_line:
                        result.append(line)

                with open(filename, 'w') as f2:
                    f2.write("".join(result))


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


def add_target_info(data, tables, targets):
    """
    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'target': 'products'}}
    >>> targets = [{ 'name': 'products', 'type': 'foo' }]

    >>> add_target_info(d, tables, targets)
    [{'data': [{'table': 'products', 'target': {'name': 'products', 'type': 'foo'}}]}]


    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'start_id': 1000}}
    >>> targets = [{ 'name': 'products', 'type': 'foo' }]

    >>> add_target_info(d, tables, targets)
    [{'data': [{'table': 'products', 'target': None}]}]


    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'target': 'products'}}
    >>> targets = [{ 'name': 'typo_products', 'type': 'foo' }]

    >>> add_target_info(d, tables, targets)
    Traceback (most recent call last):
    ConfError: target 'products' from table 'products' does not exist
    """
    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            table = y['table']
            target_name = tables[table].get('target')

            if target_name:
                target = None
                for i in targets:
                    if i['name'] == target_name:
                        target = i
                if target is None:
                    raise ConfError(
                        "target '{}' from table '{}' does not exist".format(target_name, table)
                    )

                y['target'] = copy.deepcopy(target)
            else:
                y['target'] = None
    return result

#############################################################################


def add_sql_output(data, indent=2):
    result = copy.deepcopy(data)
    for x in result:
        group = x['group']
        for y in x['data']:
            sql = sql_output_lines_for(group, y['combined'], indent)
            y['output_sql'] = sql
    return result


def sql_output_lines_for(group, attrs, indent=2):
    lines = []
    lines.append("-- facture_group_{}".format(group))
    lines.append("(")
    lines.extend(formatted_single_record_lines(attrs, indent))
    lines.append(")")
    return '\n'.join(lines)


def formatted_single_record_lines(attrs, indent):
    """ Format the record data

    >>> attrs = {\
        "id": 21000010000,\
        "classified_code": "0000001234",\
        "created_at": "2018-01-01 00:00:00",\
        "updated_at": "2018-01-01 00:00:00"\
    }
    >>> formatted_single_record_lines(attrs, 0)[0]
    '21000010000,           -- id'
    >>> formatted_single_record_lines(attrs, 0)[1]
    "'0000001234',          -- classified_code"
    >>> formatted_single_record_lines(attrs, 0)[2]
    "'2018-01-01 00:00:00', -- created_at"
    >>> formatted_single_record_lines(attrs, 0)[3]
    "'2018-01-01 00:00:00'  -- updated_at"

    >>> formatted_single_record_lines(attrs, 2)[0]
    '  21000010000,           -- id'
    """

    max_width = max([len(repr(i)) for i in attrs.values()])

    results = []
    for i in enumerate(attrs.items()):
        index = i[0]
        value = i[1][1]
        key = i[1][0]
        indent_str = ' ' * indent
        value_str = "{}".format(repr(value))
        comma_or_space = ' '
        if index < len(attrs.items()) - 1:
            comma_or_space = ','
        num_spaces_to_add = max_width - len(value_str)
        space_after = ' ' * num_spaces_to_add
        results += [indent_str + value_str + comma_or_space + space_after + ' -- ' + key]
    return results

#############################################################################


def annotate_targets_with_positional_data_from_file(targets):
    targets = copy.deepcopy(targets)
    for target in targets:
        filename = target['filename']

        data = []
        with open(filename, 'r') as f:
            data = get_facture_json_data_from_file(filename, f.read())

        start_line = None
        end_line = None

        for datum in data:
            opts = datum['data']
            if opts['target_name'] == target['name'] and opts['position'] == 'start':
                start_line = datum['linenum']

        for datum in data:
            if opts['target_name'] == target['name'] and opts['position'] == 'end':
                end_line = datum['linenum']

        if not start_line:
            raise ConfError(
                "could not find a start for target {}".format(target['name'])
            )

        if not end_line:
            raise ConfError(
                "could not find an end for target {}".format(target['name'])
            )

        target['positional_data_from_file'] = {'start_line': start_line, 'end_line': end_line}
    return targets

def validate_facture_json_data(data):
    """
    >>> file_data = '''
    ... -- facture_json: {"target_name": "products", "position": "start"}
    ... some stuff
    ... -- facture_json: {"target_name": "products", "position": "end"}
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)

    >>> file_data = '''
    ... -- facture_json: {"target_name": "items", "position": "start"}
    ... some stuff
    ... -- facture_json: {"target_name": "items", "position": "start"}
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)
    Traceback (most recent call last):
    ConfError: file 'foo.sql' starts target 'items' more than once

    >>> file_data = '''
    ... -- facture_json: {"target_name": "items", "position": "start"}
    ... some stuff
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)
    Traceback (most recent call last):
    ConfError: file 'foo.sql' starts target 'items' but does not end it

    >>> file_data = '''
    ... -- facture_json: {"target_name": "items", "position": "end"}
    ... some stuff
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)
    Traceback (most recent call last):
    ConfError: file 'foo.sql' ends target 'items' but does not start it
    """

    target_names_for_file = {}

    for d in data:
        target_names_for_file[d['filename']] = {}

    for d in data:
        if d['data']['position'] == 'start':
            if not target_names_for_file[d['filename']].get(d['data']['target_name']):
                target_names_for_file[d['filename']][d['data']['target_name']] = 0
            target_names_for_file[d['filename']][d['data']['target_name']] += 1

    for filename in target_names_for_file:
        d = target_names_for_file[filename]
        for target_name in d:
            if d[target_name] > 1:
                raise ConfError(
                    "file '{}' starts target '{}' more than once".format(filename, target_name)
                )

    for d in data:
        if d['data']['position'] == 'end':
            if not target_names_for_file[d['filename']].get(d['data']['target_name']):
                target_names_for_file[d['filename']][d['data']['target_name']] = 0
            target_names_for_file[d['filename']][d['data']['target_name']] -= 1

    for filename in target_names_for_file:
        data = target_names_for_file[filename]
        for target_name in data:
            if data[target_name] > 0:
                raise ConfError(
                    "file '{}' starts target '{}' but does not end it".format(filename, target_name)
                )
            elif data[target_name] < 0:
                raise ConfError(
                    "file '{}' ends target '{}' but does not start it".format(filename, target_name)
                )


def get_facture_json_data_from_file(filename, file_data):
    """
    >>> file_data = '''
    ... -- facture_json: {"target_name": "products", "position": "start"}
    ... some stuff
    ... -- facture_json: {"target_name": "products", "position": "end"}
    ... '''
    >>> res = get_facture_json_data_from_file('foo.sql', file_data)
    >>> len(res)
    2
    >>> res[0]['data']['position']
    'start'
    >>> res[1]['data']['position']
    'end'
    """

    results = []
    for index, line in enumerate(file_data.splitlines()):
        linenum = index + 1
        data = parse_facture_json_line(line, filename, linenum)
        if data:
            results.append({'filename': filename, 'linenum': linenum, 'data': data})
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
