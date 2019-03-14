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
            'group': 'testgroup1',
            'offset': 100,
            'data': [
                ['products p'],
            ]
        },
        {
            'group': 'testgroup2',
            'offset': 200,
            'data': [
                [
                    'products p',
                    {'attrs': {'name': 'better name'}}
                ],
            ]
        }
    ]
