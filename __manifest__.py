# -*- encoding: utf-8 -*-

{
    'name': 'FEL Megaprint',
    'version': '1.1',
    'category': 'Custom',
    'description': """ Integración con factura electrónica de Megaprint """,
    'author': 'Rodrigo Fernandez',
    'website': 'http://www.aquih.com/',
    'depends': ['fel_gt'],
    'data': [
        'views/account_views.xml',
    ],
    'assets':{
        'point_of_sale._assets_pos': [
            'fel_megaprint/static/src/**/*',
        ],
    },
    'demo': [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
