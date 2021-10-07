# -*- coding: utf-8 -*-

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID

def _mass_invoice_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_id = env['ir.module.module'].search([('name', '=', 'mass_invoicing_billing'), ('state', '=', 'installed')])
    if module_id:
        module_id.sudo().button_uninstall()
