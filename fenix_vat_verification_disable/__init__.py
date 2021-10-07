# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from . import models

from odoo import api, SUPERUSER_ID

def _vat_verification_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_id = env['ir.module.module'].search([('name', '=', 'vat_verification_disable'), ('state', '=', 'installed')])
    if module_id:
        module_id.sudo().button_uninstall()
