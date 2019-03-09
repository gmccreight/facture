def conf_tables():
    return {
        'products': {
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
