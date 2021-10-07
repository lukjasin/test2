# -*- coding: utf-8 -*-

{
    'name': 'Mass Purchase Order Merge',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Accounting/Accounting',
    'sequence': 15,
    'summary': 'Mass Purchase Order Merge',
    'depends': ['fenix_purchase_merge', 'fenix_mass_invoicing_billing'],
    'description': """
Mass Purchase Order's RFQ Merge.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/mass_account_move_views.xml',
        'views/purchase_view.xml',
    ],
    'qweb': [],
    'demo': [],
    'license': 'OPL-1',
    'post_init_hook': '_mass_po_merge_post_init',
    'installable': True,
    'auto_install': True,
}
