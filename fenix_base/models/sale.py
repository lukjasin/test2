# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_studio_pickup_address = fields.Char(string="Pickup Address", help="Order's place of collection", translate=True)
    x_studio_pickup_date = fields.Date(string="Pickup Date", help="Order's pickup date")
    sales_order_type = fields.Selection([('pickup', 'Pickup'), ('rental', 'Rental')], string="Sales Order Type")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_studio_collection = fields.Char(string="Collection", help="Product collection details", translate=True)
    x_studio_date_of_pickup = fields.Char(string="Date of Pickup", help="Product collection date", translate=True)

    def _prepare_invoice_line(self, **optional_values):
        """ Using this method update invoice line records """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({
            'x_studio_collection': self.x_studio_collection,
            'x_studio_date_of_pickup': self.x_studio_date_of_pickup,
        })
        return res
