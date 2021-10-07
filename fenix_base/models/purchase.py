# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_studio_pickup_address = fields.Char(string="Pickup Address", help="Order's place of collection", translate=True)
    x_studio_pickup_date = fields.Date(string="Pickup Date", help="Order's pickup date")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_studio_collection = fields.Char(string="Collection", help="Product collection details", translate=True)
    x_studio_date_of_pickup = fields.Char(string="Date of Pickup", help="Product collection date", translate=True)

    def _prepare_account_move_line(self, move=False):
        """ Using this method update invoice line records """
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        res.update({
            'x_studio_collection': self.x_studio_collection,
            'x_studio_date_of_pickup': self.x_studio_date_of_pickup,
        })
        return res
