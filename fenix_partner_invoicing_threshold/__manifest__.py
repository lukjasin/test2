# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Partner Invoicing Threshold',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Accounting/Accounting',
    'sequence': 15,
    'summary': 'Partner Invoicing Threshold.',
    'depends': ['sale_purchase'],
    'description': """
Set Partner Invoicing Threshold Amount.
    """,
    'data': [
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml'
    ],
    'qweb': [],
    'demo': [],
    'license': 'OPL-1',
    'post_init_hook': '_partner_invoicing_post_init',
    'installable': True,
    'auto_install': False,
}
