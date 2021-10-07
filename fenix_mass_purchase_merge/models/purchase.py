# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, models, fields
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    proforma_status = fields.Selection([('create', 'Created'), ('create_send', 'Send')], string="Proforma Status", 
        help="After merging RFQs into one Proforma with Mass Inv/Billing module, set the propper status of Proforma.\n"\
        "Created - When proforma was created with Mass Inv/Billing module\n"\
        "Send - Proforma was created and send via email or Snail Mail to the customer by Mass Inv/Billing module.\n"\
        "State not set - This means it's not proforma by Mass Inv/Billing module.", copy=False)
    proforma_date = fields.Date(string="Proforma Date", default=fields.Date.today(), copy=False)

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
