# -*- coding: utf-8 -*-

{
    'name': 'Fenix Base',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Uncategorized',
    'sequence': 16,
    'summary': 'Fenix customize odoo sh code.',
    'depends': ['sale_purchase'],
    'description': """
This Module is manage sales & purchase order collection details
    """,
    'data': [
        'views/sales_view.xml',
        'views/purchase_view.xml',
        'views/invoice_report.xml',
        'views/account_move_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
