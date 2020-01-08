import copy
import re
import collections
import json
import sys
from abc import abstractmethod

ordered_dict_version = (3, 6)
HAS_DEFAULT_ORDERED_DICT = sys.version_info > ordered_dict_version

#############################################################################


class FactureRefObj:

    @abstractmethod
    def anchors(self):
        """
        Anchors returns a list of facture anchors associated with this ref object
        :return: list[str]
        """
        pass

    @abstractmethod
    def bind(self, anchor, value):
        """
        Binds an evaluated value to an anchor
        :param anchor: str, facture anchor
        :param value: any, the resolved facture reference
        :return: void
        """
        pass

    @abstractmethod
    def eval(self):
        """
        Evaluates the reference object, returning a complete value

        This should be called once all anchors are bound in order to get the final resolved object
        :return: any, resolved facture ref object value
        """
        pass


class ConfError(Exception):
    pass


def normalize_structure(data):
    data = normalize_structure_copy_raw(data)

    data = normalize_structure_ensure_dictionaries(data)
    return data


def normalize_structure_copy_raw(data):
    """We get a certain easy-to-input structure.  Keep it in raw.

    >>> d = [{'data': [['calls c', {'attrs': {'f': 'b'}, 'refs': {'f_id': '.f.id'}}]]}]
    >>> result = normalize_structure_copy_raw(d)
    >>> [{'data': [{'raw': {'tablestr': 'calls c', 'attrs': {'f': 'b'}, 'refs': {'f_id': '.f.id'}, 'ref_objs': {}}}]}] == result
    True
    """

    result = copy.deepcopy(data)
    for x in result:
        new_data = []
        for y in x['data']:
            if len(y) == 1:
                y.append({})
            raw = {'tablestr': y[0]}
            raw.update({'attrs': y[1].get('attrs', {})})
            raw.update({'refs': y[1].get('refs', {})})
            raw.update({'ref_objs': y[1].get('ref_objs', {})})
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
    core.ConfError: in "data", "t" needs an alias
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


def consistency_checks_or_immediately_die(data, flexible_group_names=False):
    consistency_check_offset(data)
    consistency_check_no_same_aliases(data)
    consistency_check_no_incorrectly_named_groups(data, flexible_group_names=flexible_group_names)
    consistency_check_no_same_groups(data)


def consistency_check_offset(data):
    """Check whether the offsets overlap

    >>> consistency_check_offset([{'offset': 100}, {'offset': 200}])
    True

    >>> consistency_check_offset([{'offset': 100}, {'offset': 100}])
    Traceback (most recent call last):
    core.ConfError: These offsets are duplicated: {100}
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


def consistency_check_no_incorrectly_named_groups(data, flexible_group_names=False):
    if flexible_group_names:
        return True
    for x in data:
        if not re.match(r'facture_group_', x['group']):
            raise ConfError(
                'Please name groups starting with "facture_group_" or pass --flexible-group-names.'
                ' Having these longer group names allows for easy greping back to the config.'
            )
    return True


def consistency_check_no_same_groups(data):
    # TODO
    return True


#############################################################################


def enhance_with_generated_data(data, seq_for, config):
    data = add_generated_key_and_dict(data)
    data = enhance_with_generated_sequential_data(data, seq_for, config)

    data = enhance_with_referenced_foreign_ids(data)
    data = enhance_with_reference_objects(data)

    return data


def add_generated_key_and_dict(data):
    """This adds the 'generated' key and dictionary

    >>> d = [{'data': [{'table': 'calls'}]}]
    >>> result = add_generated_key_and_dict(d)
    >>> result == [{'data': [{'table': 'calls', 'generated': {}}]}]
    True
    """

    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            y['generated'] = {}
    return result


def enhance_with_generated_sequential_data(data, seq_for, table_config):
    """This enhances the data with generated ids.

    >>> seq_for = {}
    >>> d = [{'offset': 3, 'data': \
            [{'table': 'calls', 'generated': {}}]}]
    >>> config = {'calls': {'attrs': {'id': {'seq': {'start': 300}}}}}
    >>> result = enhance_with_generated_sequential_data(d, seq_for, config)
    >>> result == [{'offset': 3, 'data': [{'table': 'calls', 'generated': {'id': 303}}]}]
    True
    """

    result = copy.deepcopy(data)
    for x in result:
        offset = x['offset']
        for y in x['data']:
            attribute_names = attributes_needing_sequences(table_config[y['table']])
            for a in attribute_names:
                num, seq_for = seq_for_table_attr(y['table'], a, offset, seq_for, table_config)
                y['generated'][a] = num

    return result


def seq_for_table_attr(table, attribute, offset, seq_for, table_config):
    """Generate or update sequence numbers for each attribute that has a sequence

    >>> table_config = {'calls': {'attrs': {'id': {'seq': {'start': 300}}}}}
    >>> seq_for_table_attr('calls', 'id', 200, {}, table_config)
    (500, {'calls': {'id': 300}})
    >>> seq_for_table_attr('calls', 'id', 400, {'calls': {'id': 630}}, table_config)
    (1031, {'calls': {'id': 631}})
    """

    if seq_for == {}:
        for t in table_config:
            seq_for[t] = {}

    if seq_for[table].get(attribute):
        seq_for[table][attribute] = seq_for[table][attribute] + 1
    else:
        start = table_config[table]['attrs'][attribute]['seq']['start']
        seq_for[table][attribute] = start

    result_without_offset = seq_for[table][attribute]
    result_with_offset = result_without_offset + offset
    return result_with_offset, seq_for


def attributes_needing_sequences(table_conf):
    result = []
    for attr_name in table_conf['attrs']:
        attr_dict = table_conf['attrs'][attr_name]
        if attr_dict.get('seq'):
            result.append(attr_name)
    return result


def enhance_with_referenced_foreign_ids(data):
    """This enhances the data by adding the foreign keys to the aliases
    """
    result = copy.deepcopy(data)
    for x in result:
        group_data = x['data']
        for y in group_data:
            y['referenced'] = {}
            raw = y['raw']
            refs = raw.get('refs')
            if refs:
                for k, v in refs.items():
                    if v[0] == '.':
                        v = point_to_alias(
                                v, x['group'], group_data
                        )
                    y['referenced'][k] = v

    return result


def enhance_with_reference_objects(data):
    """This enhances the data by updating reference objects with facture anchors
    """
    result = copy.deepcopy(data)
    for x in result:
        group_data = x['data']
        for y in group_data:
            if 'referenced' not in y:
                y['referenced'] = {}
            raw = y['raw']
            ref_objs = raw.get('ref_objs')
            if ref_objs:
                for k, v in ref_objs.items():
                    for anchor in v.anchors():
                        value = point_to_alias(
                            anchor, x['group'], group_data
                        )
                        v.bind(anchor, value)
                    y['referenced'][k] = v.eval()
    return result


def point_to_alias(refstr, group_name, group_data):
    """ Given a refstr, get attribute value in target.

    >>> d = [{'alias': 'p', 'generated': {'id': 231}}]

    >>> point_to_alias('.p.id', 'z', d)
    231

    >>> point_to_alias('.id', 'z', d)
    Traceback (most recent call last):
    core.ConfError: refstr ".id" incorrectly formatted in group "z"

    >>> point_to_alias('.x.id', 'z', d)
    Traceback (most recent call last):
    core.ConfError: refstr: alias "x" does not exist in group "z"

    >>> point_to_alias('.p.y', 'z', d)
    Traceback (most recent call last):
    core.ConfError: key "y" missing for alias "p" in group "z"
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

    >>> result = add_table_defaults(d, c)
    >>> result == [{'data': [{'table': 'calls', 'defaults': {'foo': 'bar'}}]}]
    True

    >>> d = [{'data': [{'table': 'whoops'}]}]
    >>> c = {'calls': {'attrs': {'foo': {'default': 'bar'}}}}

    >>> add_table_defaults(d, c)
    Traceback (most recent call last):
    core.ConfError: table "whoops" has no default attrs conf
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
            'There were overlapping keys in merging dictionaries: {}, {}'.format(d1, d2)
        )
    else:
        d1.update(d2)
        return d1


def combine_all_into_result(data):
    result = copy.deepcopy(data)
    for x in result:
        for y in x['data']:
            z = y['defaults']
            z.update(y['referenced'])
            for attr in y['raw']['attrs']:
                z.update({attr: y['raw']['attrs'][attr]})
            z = careful_merge_dicts(z, y['generated'])
            y['combined'] = z
    return result


def add_target_info(data, tables, targets):
    """
    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'target': 'products'}}
    >>> targets = [{ 'name': 'products', 'type': 'foo' }]

    >>> result = add_target_info(d, tables, targets)
    >>> result == [{'data': [{'table': 'products', 'target': {'name': 'products', 'type': 'foo'}}]}]
    True

    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'start_id': 1000}}
    >>> targets = [{ 'name': 'products', 'type': 'foo' }]

    >>> result = add_target_info(d, tables, targets)
    >>> result == [{'data': [{'table': 'products', 'target': None}]}]
    True

    >>> d = [{'data': [{'table': 'products'}]}]
    >>> tables = {'products': {'target': 'products'}}
    >>> targets = [{ 'name': 'typo_products', 'type': 'foo' }]

    >>> add_target_info(d, tables, targets)
    Traceback (most recent call last):
    core.ConfError: target 'products' from table 'products' does not exist
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


def add_sql_output(data, conf_tables, indent=2):
    result = copy.deepcopy(data)
    for x in result:
        group = x['group']
        for y in x['data']:
            attrs_ordered = collections.OrderedDict()
            ordered_attrs = conf_tables[y['table']]['attrs']
            if not HAS_DEFAULT_ORDERED_DICT and not isinstance(ordered_attrs, collections.OrderedDict):
                raise ConfError(
                    """table '{}' has unordered attrs. when using a version of python < 3.6 the attrs must be in 
                    a collection.OrderedDict""".format(y['table'])
                )
            for i in list(ordered_attrs):
                attrs_ordered[i] = y['combined'][i]
            sql = sql_output_lines_for(group, attrs_ordered, indent)
            y['output_sql'] = sql
    return result


def sql_output_lines_for(group, attrs, indent=2):
    lines = []
    lines.append("-- {}".format(group))
    lines.append("(")
    lines.extend(formatted_single_record_lines(attrs, indent))
    lines.append(")")
    return '\n'.join(lines)


def formatted_single_record_lines(attrs, indent):
    """ Format the record data

    >>> attrs = collections.OrderedDict([\
        ("id", 21000010000),\
        ("job_run_id", {"raw": "$build_id"}),\
        ("classified_code", "0000001234"),\
        ("created_at", "2018-01-01 00:00:00"),\
        ("updated_at", "2018-01-01 00:00:00")\
    ])
    >>> formatted_single_record_lines(attrs, 0)[0]
    '21000010000,           -- id'
    >>> formatted_single_record_lines(attrs, 0)[1]
    '$build_id,             -- job_run_id'
    >>> formatted_single_record_lines(attrs, 0)[2]
    "'0000001234',          -- classified_code"
    >>> formatted_single_record_lines(attrs, 0)[3]
    "'2018-01-01 00:00:00', -- created_at"
    >>> formatted_single_record_lines(attrs, 0)[4]
    "'2018-01-01 00:00:00'  -- updated_at"

    >>> formatted_single_record_lines(attrs, 2)[0]
    '  21000010000,           -- id'

    """

    with_value_str = []
    for i in attrs.items():
        key = i[0]
        value = i[1]

        value_str = ''
        if isinstance(value, dict):
            if not value.get('raw'):
                raise ConfError(
                    "value is dict but no raw key {}".format(value)
                )
            value_str = value['raw']
        else:
            value_str = "{}".format(repr(value))

        with_value_str.append({'key': i[0], 'value': value, 'value_str': value_str})

    max_width = max([len(i['value_str']) for i in with_value_str])

    results = []
    for i in enumerate(with_value_str):
        index = i[0]
        key = i[1]['key']
        value_str = i[1]['value_str']

        indent_str = ' ' * indent
        comma_or_space = ' '
        if index < len(attrs.items()) - 1:
            comma_or_space = ','
        num_spaces_to_add = max_width - len(value_str)
        space_after = ' ' * num_spaces_to_add
        results += [indent_str + value_str + comma_or_space + space_after + ' -- ' + key]
    return results

#############################################################################


def write_to_actual_target_files(targets):
    targets = targets_sorted_by_start_descending(targets)
    for target in targets:
        payload = "\n" + ",\n\n".join(target['output_values']) + "\n\n"
        filename = target['filename']
        start = target['positional_data_from_file']['start_line']
        end = target['positional_data_from_file']['end_line']
        insert_string_into_file_between_lines(payload, filename, start, end)


def targets_sorted_by_start_descending(targets):
    targets = copy.deepcopy(targets)
    targets.sort(key=lambda x: x["positional_data_from_file"]["start_line"], reverse=True)
    return targets


def insert_string_into_file_between_lines(string, filename, start, end):
    result = []
    with open(filename, 'r') as f:
        for index, line in enumerate(f):
            linenum = index + 1
            if linenum <= start:
                result.append(line)
            if linenum == start + 1:
                result.append(string)
            if linenum >= end:
                result.append(line)

    with open(filename, 'w') as f:
        f.write("".join(result))


def annotate_targets_with_output_values(targets, data):
    targets = copy.deepcopy(targets)

    for target in targets:
        target['output_values'] = []

    for x in data:
        for y in x['data']:
            target = target_with_name(targets, y['target']['name'])
            target['output_values'].append(y['output_sql'])

    return targets


def target_with_name(targets, name):
    for i in targets:
        if i['name'] == name:
            return i
    return None


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
            opts = datum['data']
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
    core.ConfError: file 'foo.sql' starts target 'items' more than once

    >>> file_data = '''
    ... -- facture_json: {"target_name": "items", "position": "start"}
    ... some stuff
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)
    Traceback (most recent call last):
    core.ConfError: file 'foo.sql' starts target 'items' but does not end it

    >>> file_data = '''
    ... -- facture_json: {"target_name": "items", "position": "end"}
    ... some stuff
    ... '''
    >>> data = get_facture_json_data_from_file('foo.sql', file_data)
    >>> validate_facture_json_data(data)
    Traceback (most recent call last):
    core.ConfError: file 'foo.sql' ends target 'items' but does not start it
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
    core.ConfError: facture_json on line 34 in './foo.sql' is not valid JSON
    """

    m = re.match(r'.*facture_json: (.*)', line)
    if m:
        json_text = m.group(1)
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

