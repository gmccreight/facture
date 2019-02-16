# This configuration file is written in Python so you can use variables, code,
# etc.


def table_config():
    default_date = '2018-01-01 00:00:00'
    return {
        'products': {
            'start_id': 21000000000,
            'attrs': {
                'classified_code': {'default': '0000001234'},
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        },
        'retailer_products': {
            'start_id': 22000000000,
            'attrs': {
                'product_id': {},
                'retailer_id': {},
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        },
        'warehouses': {
            'start_id': 23000000000,
            'attrs': {
                'created_at': {'default': default_date},
                'updated_at': {'default': default_date}
            }
        }
    }


def data():
    return [
        {
            'group': 'costco_full_control',
            'offset': 10000,
            'data': [
                ['warehouses w'],
                ['products p1'],
                ['products p2'],
                [
                    'retailer_products rp1',
                    {'attrs': {'retailer_id': '.w.id', 'product_id': '.p1.id'}}
                ],
                [
                    'retailer_products rp2',
                    {'attrs': {'retailer_id': '.w.id', 'product_id': '.p2.id'}}
                ]
            ]
        },
        {
            'group': 'costco_full_control_2',
            'offset': 1000,
            'data': [
                ['warehouses w'],
                ['products p'],
                [
                    'retailer_products rp',
                    {'attrs': {'retailer_id': '.w.id', 'product_id': '.p.id'}}
                ]
            ]
        }
    ]
