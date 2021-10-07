# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, models, fields
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or list()
        domain = list()
        if self._context.get('po_domain') and self._context.get('group_partner_id'):
            domain = expression.AND(
                [domain.append(literal_eval(self._context['po_domain'])),
                [('partner_id', '=', self._context['group_partner_id'])]]
            )
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or list()
        if self._context.get('po_domain') and self._context.get('group_partner_id'):
            domain = expression.AND(
                [domain.append(literal_eval(self._context['po_domain'])),
                [('partner_id', '=', self._context['group_partner_id'])]]
            )
        return super(PurchaseOrder, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
