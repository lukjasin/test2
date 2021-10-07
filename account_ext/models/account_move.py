# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        vals = super(AccountMove, self).action_invoice_sent()
        vals.get('context').update({'default_snailmail_is_letter': self.partner_id.x_studio_paper_invoice})
        return vals


# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     x_studio_paper_invoice = fields.Boolean('Paper Invoice')