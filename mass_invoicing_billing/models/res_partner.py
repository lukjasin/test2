# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.tools import float_compare


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.depends('sale_order_ids', 'sale_order_ids.amount_total', 'sale_order_ids.company_id')
    # def _compute_with_threshold(self):
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     for partner in self:
    #         partner.with_threshold = False
    #         if partner.invoicing_threshold_amount:
    #             amount_total = sum(partner.sale_order_ids.filtered(
    #                 lambda order: order.state in ('draft', 'sent', 'sale') and order.company_id.id in (
    #                     self._context.get('allowed_company_ids') or self.env.company.ids
    #                 )
    #             ).mapped('amount_total'))
    #             if not float_compare(amount_total, partner.invoicing_threshold_amount, precision_digits=precision) < 0:
    #                 partner.with_threshold = True

    paper_invoice = fields.Boolean(string="Paper Invoice", copy=False)
    invoicing_method = fields.Selection([
        ('proforma', "Proforma"),
        ('selfinvoice', "Self Invoice"),
    ], string="Invoicing Method", copy=False)
    # with_threshold = fields.Boolean(string="Use Threshold Amount", compute="_compute_with_threshold", store=True)
