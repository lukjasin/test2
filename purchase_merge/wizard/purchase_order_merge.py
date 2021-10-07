# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrderMerge(models.TransientModel):
    _name = 'purchase.order.merge'
    _description = 'Purchase Order Merge'

    po_merge_type = fields.Selection([
            ('cancel_new_po', "Create new order and cancel all selected purchase orders"),
            ('delete_new_po', "Create new order and delete all selected purchase orders"),
            ('cancel_add_po', "Merge order on existing selected order and cancel others"),
            ('delete_add_po', "Merge order on existing selected order and delete others")],
            default='cancel_new_po', string="Merge Type", required=True)
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Order')

    def merge_purchase_orders(self):
        self.ensure_one()
        PurchaseOrder = self.env['purchase.order']
        new_po_id = False

        def _merge_purchase_order(purchase_orders, new_po):
            for order in purchase_orders:
                for line in order.order_line:
                    existing_po_line_id = False
                    for new_po_line in new_po.order_line:
                        if line.product_id.id == new_po_line.product_id.id\
                            and line.price_unit == new_po_line.price_unit and line.x_studio_date_of_pickup == new_po_line.x_studio_date_of_pickup \
                            and line.x_studio_collection == new_po_line.x_studio_collection:
                            existing_po_line_id = new_po_line
                            break
                    if existing_po_line_id:
                        existing_po_line_id.product_qty += line.product_qty
                        existing_po_line_id.taxes_id = [(4, tax.id) for tax in line.taxes_id]
                    else:
                        line.copy(default={'order_id': new_po.id})

        purchase_order_ids = PurchaseOrder.browse(self._context.get('active_ids', []))
        if len(purchase_order_ids.ids) < 2:
            raise ValidationError(_("Please select more then one purchase order for merge operation."))
        if any(purchase_order_ids.filtered(lambda po: po.state != 'draft')):
            raise ValidationError(_("Please select purchase orders which are in RFQ state."))
        if not len(purchase_order_ids.mapped('partner_id').ids) == 1:
            raise ValidationError(_('Please select purchase orders of same Vendors.'))

        if self.po_merge_type in ['cancel_new_po', 'delete_new_po']:
            new_po_id = PurchaseOrder.create({'partner_id': purchase_order_ids[0].partner_id.id})
            _merge_purchase_order(purchase_order_ids, new_po_id)
            purchase_order_ids.button_cancel()
            if self.po_merge_type == 'delete_new_po':
                purchase_order_ids.sudo().unlink()

        if self.po_merge_type in ['cancel_add_po', 'delete_add_po']:
            new_po_id = self.purchase_order_id
            purchase_orders = purchase_order_ids.filtered(lambda po: po.id != self.purchase_order_id.id)
            _merge_purchase_order(purchase_orders, new_po_id)
            purchase_orders.button_cancel()
            if self.po_merge_type == 'delete_add_po':
                purchase_orders.sudo().unlink()
        return new_po_id
