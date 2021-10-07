# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Disable Contact VAT Verification',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Accounting/Accounting',
    'sequence': 15,
    'summary': 'Disable Contact VAT Verification.',
    'depends': ['base_vat'],
    'description': """
Disable Contact VAT Verification.
    """,
    'data': [
        'data/ir_config_data.xml',
        'views/res_config_settings_views.xml'
    ],
    'qweb': [],
    'demo': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
