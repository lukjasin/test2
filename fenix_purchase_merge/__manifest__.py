# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Purchase Order Merge',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Inventory/Purchase',
    'sequence': 15,
    'summary': 'Purchase Order Merge.',
    'depends': ['fenix_base'],
    'description': """
RFQs Purchase Order Merge.
    """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_order_merge_view.xml',
    ],
    'qweb': [],
    'demo': [],
    'license': 'OPL-1',
    'post_init_hook': '_purchase_merge_post_init',
    'installable': True,
    'application': False,
    'auto_install': False,
}
