# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_studio_collection = fields.Char(string="Collection", help="Product collection details", translate=True)
    x_studio_date_of_pickup = fields.Char(string="Date of Pickup", help="Product collection date", translate=True)
