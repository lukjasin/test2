# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models, _
from odoo.tools import groupby
from odoo.exceptions import ValidationError


class MassAccountMove(models.Model):
    _inherit = 'mass.account.move'

    is_generate_proforma = fields.Boolean(string="Generate Proforma", copy=False, default=False,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Automatically generate proforma by order merge configuration.")
    po_merge_type = fields.Selection([
        ('cancel_new_po', "Create new order and cancel all selected purchase orders"),
        ('delete_new_po', "Create new order and delete all selected purchase orders"),
        ('cancel_add_po', "Merge order on existing selected order and cancel others"),
        ('delete_add_po', "Merge order on existing selected order and delete others")],
        default='cancel_new_po', string="Merge Type",
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]})
    partner_purchase_order_ids = fields.One2many(comodel_name='partner.purchase.order', inverse_name='mass_account_move_id')

    @api.onchange('po_merge_type', 'is_generate_proforma', 'domain', 'model_id')
    def _onchange_po_merge_type(self):
        is_merge_partner_po = (self.is_generate_proforma and self.po_merge_type in ('cancel_add_po', 'delete_add_po'))
        partner_po = [(5, 0, 0)]
        if is_merge_partner_po and self.model_name == 'purchase.order':
            orders = self.env['purchase.order'].search(self._parse_domain())
            partner_po_vals = lambda partner, order: dict(
                partner_id=partner.id,
                purchase_order_id=order.id
            )
            for partner_id, order_ids in groupby(orders, key=lambda o: o[self._get_partner_field()]):
                partner_po.append(
                    (0, 0, partner_po_vals(partner_id, order_ids[0]))
                )
        self.partner_purchase_order_ids = partner_po

    def _get_proforma_template_attachment(self, order, report, report_name):
        result, format = report._render_qweb_pdf([order.id])
        return self.env['ir.attachment'].create(dict(
            name=report_name,
            datas=base64.b64encode(result),
            res_model='mail.compose.message',
            res_id=0,
            type='binary'
        ))

    def _action_rfq_send(self, order):
        self.ensure_one()

        partner = order.partner_id
        if self._is_sent_unnecessary(partner):
            return False

        is_sent_mail = self._is_sent_mail(partner)
        if is_sent_mail and (not self._is_valid_partner_email(partner)):
            raise ValidationError(_("\nOrder '%s' is failed to send by email because of email address is not available." % (
                order.display_name
            )))

        if is_sent_mail:
            MailComposeMessage = self.env['mail.compose.message']
            try:
                template_id = self.env['ir.model.data'].get_object_reference('purchase', 'email_template_edi_purchase')[1]
            except ValueError:
                template_id = False
            ctx = dict(self.env.context or {})
            ctx.update(dict(
                default_model='purchase.order',
                active_model='purchase.order',
                active_id=order.ids[0],
                active_ids=order.ids,
                default_res_id=order.ids[0],
                default_use_template=bool(template_id),
                default_template_id=template_id,
                default_composition_mode='comment',
                custom_layout="mail.mail_notification_paynow",
                force_email=True,
                mark_rfq_as_sent=True,
                model_description=_('Request for Quotation'),
                quotation_only=True,
                send_rfq=True,
            ))

            # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
            # object. Therefore, we pass the model description in the context, in the language in which
            # the template is rendered.
            lang = self.env.context.get('lang')
            if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
                template = self.env['mail.template'].browse(ctx['default_template_id'])
                if template and template.lang:
                    lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

            self = self.with_context(lang=lang)
            mail_compose_message_id = MailComposeMessage.with_context(ctx).create({
                'template_id': template_id
            })
            report = self.env['ir.actions.report']._get_report_from_name('purchase.report_purchaseorder_copy_1')
            mail_compose_message_id.onchange_template_id_wrapper()
            if report and mail_compose_message_id.template_id and self.move_confirmation == 'create_confirm_sent':
                report_name = mail_compose_message_id.template_id._render_field(
                    'report_name', [order.id]
                )[order.id]
                attachment_id = self._get_proforma_template_attachment(
                    order, report, report_name
                )
                mail_compose_message_id.attachment_ids = [(6, 0, attachment_id.ids)]
            mail_compose_message_id.send_mail()
            return True
        return False

    def _create_purchase_order_merge(self, new_po=False):
        self.ensure_one()
        return self.env['purchase.order.merge'].create(dict(
            po_merge_type=self.po_merge_type,
            purchase_order_id=new_po and new_po.id
        ))

    def _action_purchase_order_move_create(self, orders, **kw):
        moves = super(MassAccountMove, self)._action_purchase_order_move_create(orders, **kw)
        orders = orders.filtered(lambda order: order.state == 'draft')
        if orders:
            # conditions
            confirm_by_policy = (self.is_auto_confirm and self.confirm_by == 'policy')
            is_proforma = (orders[0].partner_id.invoicing_method in ('proforma', False))
            is_merge_selected_po = self.po_merge_type in ('cancel_add_po', 'delete_add_po')
            is_confirm_necessary = self.move_confirmation in ('create_confirm', 'create_confirm_sent')

            if confirm_by_policy and is_proforma and self.is_generate_proforma and self.is_grouped_move:
                partner_id = orders[0].partner_id
                new_po = is_merge_selected_po and self.partner_purchase_order_ids.filtered(
                    lambda p: p.partner_id.id == partner_id.id
                )
                new_order = False
                if len(orders.ids) == 1:
                    new_order = orders[0]
                if not new_order:
                    po_merge_id = self._create_purchase_order_merge(new_po=new_po and new_po.purchase_order_id)
                    new_order = po_merge_id.with_context(active_ids=orders.ids).merge_purchase_orders()
                if is_confirm_necessary and new_order:
                    new_order.button_confirm()
                self._action_rfq_send(new_order)
        return moves
