# -*- coding: utf-8 -*-

from odoo import fields, models


class PartnerPurchaseOrder(models.Model):
    _name = 'partner.purchase.order'
    _description = "Partner Purchase Order"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(comodel_name='res.partner', string="Vendor", copy=False)
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string="Purchase Order")
    mass_account_move_id = fields.Many2one(comodel_name='mass.account.move', string="Mass Account Move")
