# -*- coding: utf-8 -*-

{
    'name': 'Fenix Custom Reports',
    'version': '1.0',
    'author': '',
    'website': '',
    'category': 'Uncategorized',
    'sequence': 16,
    'summary': 'Fenix customize odoo sh code.',
    'depends': ['account'],
    'description': """
This Module is manage report of odoo sh.
    """,
    'data': [
        'report/vendor_report.xml',
        'views/invoice_report.xml',
        'data/mail_template_data.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
