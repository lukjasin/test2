# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_vat_verification = fields.Boolean(string='Disable VAT Verification',
    	config_parameter='fenix_vat_verification_disable.disable_vat_verification')
