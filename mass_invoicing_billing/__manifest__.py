# -*- coding: utf-8 -*-

{
    'name': 'Mass Invoicing/Billing',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Accounting/Accounting',
    'sequence': 15,
    'summary': 'Mass Invoicing/Billing',
    'depends': ['partner_invoicing_threshold', 'account_accountant', 'snailmail_account'],
    'description': """
Mass Creation of Invoicing/Billing.
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_cron_data.xml',
        'wizard/mass_account_move_schedule_views.xml',
        'views/assets_registry.xml',
        'views/res_partner_view.xml',
        'views/mass_account_move_views.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
