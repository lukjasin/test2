# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        disable_vat_verification = self.env["ir.config_parameter"].sudo()\
                .get_param("vat_verification_disable.disable_vat_verification")
        if disable_vat_verification:
            return
        return super(ResPartner, self).check_vat()
