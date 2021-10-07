# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo.osv import expression
from odoo.tools import groupby as groupBy
from odoo.tools import float_compare

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    threshold_partner_id = fields.Many2one(comodel_name='res.partner', related='partner_id', store=True,
        help="Technical field used for check threshold filter")
    threshold_wo_email_partner_id = fields.Many2one(comodel_name='res.partner', related='partner_id', store=True,
        help="Technical field used for check threshold without set email filter")

    def _check_is_partner_wo_invoicing_threshold(self, group_partner):
        return (float_compare(
            sum(self.filtered(lambda po: po.partner_id.id == group_partner.id).mapped('amount_total')),
            group_partner.invoicing_threshold_amount,
            precision_digits=self.env['decimal.precision'].precision_get('Product Unit of Measure')
        ) < 0)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        def groupby_orders():
            orders_by_partner = list()
            for partner_id, orders in groupBy(self.search(domain, order=orderby), key=lambda order: order.partner_id):
                orders_by_partner += [(partner_id, self.concat(*orders))]
            return orders_by_partner

        if 'threshold_partner_id' in groupby:
            order_without_threshold = self
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            for partner_id, purchase_order_ids in groupby_orders():
                if partner_id.invoicing_threshold_amount and\
                    purchase_order_ids._check_is_partner_wo_invoicing_threshold(partner_id):
                    order_without_threshold |= purchase_order_ids
            domain = expression.AND([domain, [('id', 'not in', order_without_threshold.ids)]])

        if 'threshold_wo_email_partner_id' in groupby:
            threshold_without_email = self
            for partner_id, purchase_order_ids in groupby_orders():
                if partner_id.invoicing_threshold_amount and\
                    not purchase_order_ids._check_is_partner_wo_invoicing_threshold(partner_id):
                    threshold_without_email |= purchase_order_ids.filtered(lambda x: not x.partner_id.email and x.invoice_status == 'to invoice')
            domain = expression.AND([domain, [('id', 'in', threshold_without_email.ids)]])

        return super(PurchaseOrder, self).read_group(domain=domain, fields=fields, groupby=groupby,
                                            offset=offset, limit=limit, orderby=orderby, lazy=lazy)
