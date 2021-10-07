# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, models, fields
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if self._context.get('merge_po', False) and self._context.get('order_ids'):
            domain = [('id', 'in', self._context['order_ids'])]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []
        if self._context.get('merge_po', False) and self._context.get('order_ids'):
            domain = expression.AND([domain, [('id', 'in', self._context['order_ids'])]])
        return super(PurchaseOrder, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
