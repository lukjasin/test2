# -*- coding: utf-8 -*-

import xlsxwriter
import base64
import logging

from io import BytesIO
from ast import literal_eval

from odoo.osv import expression

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import get_lang
from odoo.tools import groupby

_logger = logging.getLogger(__name__)


class MassAccountMove(models.Model):
    _name = 'mass.account.move'
    _description = "Mass Account Move"
    _inherit = ['mail.thread']

    @api.depends('model_id', 'domain')
    def _compute_partner_count(self):
        for mass_acc_move in self:
            Model = self.env[mass_acc_move.model_id.model]
            mass_acc_move.partner_count = len(Model.search(
                    mass_acc_move._parse_domain()
                ).mapped('partner_id'))

    name = fields.Char(string="Name", required=True,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', ondelete='cascade', required=True,
        domain=[('model', 'in', ['sale.order', 'purchase.order'])],
        default=lambda self: self.env.ref('sale.model_sale_order').id,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    model_name = fields.Char(
        string='Recipients Model Name', related='model_id.model',
        readonly=True, related_sudo=True)
    domain = fields.Char(string='Domain', default="[]",
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    pre_check_errors = fields.Boolean(string="Pre Check Errors", copy=False, default=True,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Check errors related invoices/bills in advance before generating it.")
    is_auto_confirm = fields.Boolean(string="Auto Confirm", copy=False, default=False,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Automatically confirm non-confirmed order.")
    confirm_by = fields.Selection([
            ('policy', "Vendor's Policy"),
            ('force', "Forcefully"),
        ], string="Confirm By", copy=False, default='policy',
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Confirm orders by vendor's invoicing policy or forcefully.")
    is_grouped_move = fields.Boolean(string="Grouped Move", copy=False, default=True,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Generate only one invoice per customer.")
    partner_with_threshold = fields.Boolean(string="partner with threshold", copy=False, default=True,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Generate Invoice/Bills only for Customer/Vendor with threshold.")
    move_confirmation = fields.Selection([
            ('create', "Create Only"),
            ('create_sent', "Create and Sent"),
            ('create_confirm', "Create and Confirm"),
            ('create_confirm_sent', "Create, Confirm and Sent"),
        ], string="Invoice Confirmation", copy=False, required=True, default='create',
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Choose what to do with created invoice/bills.")
    sent_option = fields.Selection([
            ('cust_settings', "Based on Customer Settings"),
            ('mail', "Sent mail only"),
            ('snailmail', "Sent snailmail only"),
            ('mail_snailmail', "Sent mail and snailmail"),
            ('not_sent', "Do not sent"),
        ], string="Email / Snailmail", copy=False, required=True, default='cust_settings',
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    state = fields.Selection([
        ('start', 'Start'),
        ('scheduled', 'Scheduled'),
        ('processed', 'Processed'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, tracking=True, copy=False, default='start')
    partner_count = fields.Integer(string="Partners Count",
        compute='_compute_partner_count', readonly=True, store=True)
    processed_partner_ids = fields.Many2many("res.partner",
        'mass_account_move_processed_partner_rel', 'mass_acc_m_id', 'partner_id',
        string="Processed Partners")
    user_id = fields.Many2one(comodel_name='res.users', string="Responsible", default= lambda self: self.env.user,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    company_id = fields.Many2one(comodel_name='res.company', string="Company", default=lambda self: self.env.company,
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    schedule_date = fields.Datetime(string="Scheduled On",
        states={'scheduled': [('readonly', True)], 'processed': [('readonly', True)], 'cancel': [('readonly', True)]},)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True, tracking=True)
    account_move_history_ids = fields.One2many(comodel_name='mass.account.move.history', inverse_name='mass_account_move_id')
    # account_move_mail_history_ids = fields.One2many(comodel_name='mass.account.move.history', inverse_name='mass_account_move_mail_id')
    filename = fields.Char(string='File Name')
    excel_file = fields.Binary(string='Excel Report File', readonly=True)

    # // ORM Methods
    def unlink(self):
        if any(self.filtered(lambda move: move.state in ('scheduled', 'processed'))):
            raise ValidationError(_("You can not delete Mass Invoicing / Billing in Scheduled or Processed state."))
        return super(MassAccountMove, self).unlink()

    # // misc
    def _get_move_string(self):
        return (self.model_name == "sale.order" and _("Invoice")
            or self.model_name == "purchase.order" and _("Bill")
            or _("Transaction"))

    def _get_partner_string(self):
        return (self.model_name == "sale.order" and _("Customer")
            or self.model_name == "purchase.order" and _("Vendor")
            or _("Partner"))

    def _get_partner_field(self):
        return self.model_id.model in ('sale.order', 'purchase.order') and 'partner_id' or False

    def _parse_domain(self):
        self.ensure_one()
        try:
            domain = literal_eval(self.domain) if self.domain else list()
        except Exception:
            domain = [('id', 'in', [])]
        return domain

    def _create_history(self, values):
        self.ensure_one()
        return self.env['mass.account.move.history'].create(dict(
            # name='%s,%s' % (order._name, str(order.id)),
            name=values.get('name', '---'),
            message=values.get('message', '---'),
            record_status=values.get('status', 'fail'),
            mass_account_move_id=self.id,
            partner_id=values.get('partner_id', False),
        ))

    def _handle_logs(self, partner, logs):
        self.ensure_one()
        if not logs:
            return True

        error_logs = list(filter(lambda log: not ('self_log' in log), logs))
        if error_logs:
            transaction_name = self._get_move_string()
            partner_msg = ''
            logger_msg = ''
            for log in error_logs:
                self._create_history({**log, 'partner_id': partner.id,})
                name = log.get('name')
                message = log.get('message')

                partner_msg += '''<dt class="col-sm-2">%s</dt>
                    <dd class="col-sm-10">%s</dd>''' % (name, message)
                logger_msg += '\n%s\t%s' % (name, message)
            partner.message_post(body='''<span class="text-danger">{title}</span>
                <dl class="row">{msg}</dl>'''.format(
                    title=_("Your %s(s) is failed processing due to below reason(s).") % transaction_name,
                    msg=partner_msg
                ))
            _logger.error('''{transaction}(s) is failed processing for {partner}, {msg}'''.format(
                    transaction=transaction_name, partner=partner.display_name, msg=logger_msg
                ))

        self_logs = list(filter(lambda log: log.get('self_log', False), logs))
        if self_logs:
            self_msg = ''
            for log in self_logs:
                self_msg += '''<dt class="col-sm-6">%s: %s</dt>
                    <dd class="col-sm-6">%s</dd>''' % (
                        self._get_partner_string(),
                        log.get('name', '---'),
                        log.get('message', '---')
                    )
            self.message_post(body='''
                <dl class="row">{msg}</dl>'''.format(
                    msg=self_msg
                ))

        return True

    def generate_history(self):
        self.ensure_one()
        try:
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            _add_format = lambda formate_dict: workbook.add_format(formate_dict)
            sub_heading_format = _add_format(dict(
                align='center', border=1, bold=True,
                size=18, bg_color='#D3D3D3'
            ))
            cell_heading_format = _add_format(dict(
                align='center', bold=True, border=1,
                size=12, bg_color='#D3D3D3'
            ))
            cell_date_format = _add_format(dict(border=1, size=10, num_format='yyyy-mm-dd hh:mm:ss', align='center'))
            cell_data_format = _add_format(dict(border=1, size=10, align='center'))
            cell_message_format = _add_format(dict(border=1, size=10))
            worksheet = workbook.add_worksheet(self.name)

            row, column = 1, 0
            worksheet.merge_range('A%s:E%s' % (row, row+1), (self.name + ' %s' % fields.Datetime.now()), sub_heading_format)
            row += 2
            worksheet.set_column('A:A', 12)
            worksheet.set_column(1, 2, 20)
            worksheet.set_column('D:D', 40, None, {'collapsed': 1})
            worksheet.set_column('E:E', 30)

            write_worksheet = lambda row, col, data, sformat: worksheet.write(row, col, data, sformat)

            write_worksheet(row, column, 'SN', cell_heading_format)
            write_worksheet(row, column, 'SN', cell_heading_format)
            write_worksheet(row, column+1, 'Record [ID]', cell_heading_format)
            write_worksheet(row, column+2, 'Partner', cell_heading_format)
            write_worksheet(row, column+3, 'Message', cell_heading_format)
            write_worksheet(row, column+4, 'Date', cell_heading_format)

            row += 1
            for num, history in enumerate(self.account_move_history_ids, 1):
                write_worksheet(row, column, str(num), cell_data_format)
                write_worksheet(row, column+1, history.name, cell_message_format)
                write_worksheet(row, column+2, history.partner_id.display_name, cell_data_format)
                write_worksheet(row, column+3, history.message, cell_message_format)
                write_worksheet(row, column+4, history.create_date, cell_date_format)
                row += 1
        except Exception as e:
            error_message = _('Something went wrong while generating file!\n\n%s ' % str(e))
            _logger.exception(error_message)
            raise ValidationError(error_message)
        workbook.close()
        self.write({
            'filename': '%s.xlsx' % (self.name.lower().replace(' ', '_')),
            'excel_file': base64.encodebytes(fp.getvalue())
        })
        fp.close()

    # // automated action
    @api.model
    def _process_mass_account_move_queue(self):
        mass_account_moves = self.search([
            ('state', '=', 'scheduled'),
            ('schedule_date', '<', fields.Datetime.now())
        ])
        for ma in mass_account_moves:
            ma.button_process()
        return True


    # // email/snail mail sent actions
    def _is_sent_unnecessary(self, partner):
        return ((self.move_confirmation not in ('create_sent', 'create_confirm_sent'))
            or (self.sent_option == 'not_sent'))

    def _is_sent_mail(self, partner):
        return ((self.sent_option == 'cust_settings' and not partner.paper_invoice)
            or self.sent_option in ('mail', 'mail_snailmail'))

    def _is_sent_snailmail(self, partner):
        return ((self.sent_option == 'cust_settings' and partner.paper_invoice)
            or self.sent_option in ('snailmail', 'mail_snailmail'))

    def _is_valid_partner_email(self, partner):
        return partner.email or False

    def _is_valid_partner_snailmail(self, partner):
        return self.env['snailmail.letter']._is_valid_address(partner)

    def _action_sent_move(self, move):
        partner = move.partner_id
        if self._is_sent_unnecessary(partner):
            return False

        error_message = ""
        is_sent_snailmail = self._is_sent_snailmail(partner)
        if is_sent_snailmail and (not self._is_valid_partner_snailmail(partner)):
            error_message += _("%s '%s' is failed to send by post because of address is not complete." % (
                    self._get_move_string(), move.display_name
                ))

        is_sent_mail = self._is_sent_mail(partner)
        if is_sent_mail and (not self._is_valid_partner_email(partner)):
            error_message += _("\n%s '%s' is failed to send by email because of email address is not available." % (
                    self._get_move_string(), move.display_name
                ))

        if error_message:
            raise ValidationError(error_message)

        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)

        lang = False
        if template:
            lang = template._render_lang(move.ids)[move.id]
        if not lang:
            lang = get_lang(self.env).code

        AccountInvoiceSend = self.env['account.invoice.send']
        ctx = dict(
            default_model='account.move',
            default_res_id=move.id,
            active_ids=move.ids,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).name,
            force_email=True
        )

        values = dict(
            is_print=False,
            is_email=is_sent_mail,
            snailmail_is_letter=is_sent_snailmail,
        )

        send_snailmail_after_mail = False
        if values.get('is_email', False) and values.get('snailmail_is_letter', False):
            send_snailmail_after_mail = values.pop('snailmail_is_letter')

        account_invoice_send_id = AccountInvoiceSend.with_context(ctx).create(values)
        res = account_invoice_send_id.send_and_print_action()

        if send_snailmail_after_mail:
            account_invoice_send_id.write(dict(snailmail_is_letter=send_snailmail_after_mail))
            res = account_invoice_send_id.send_and_print_action()

        if res and isinstance(res, dict):
            res_id = res.get('res_id', False)
            res_model = res.get('res_model', False)
            if res_id and (res_model and (res_model == 'snailmail.confirm.invoice')):
                self.env[res_model].browse(res_id).action_confirm()
        return res

    def action_sent_move(self, moves):
        for move in moves:
            self._action_sent_move(move)
        return True

    # // object specific generate move actions
    def _action_sale_order_move_create(self, orders, **kw):
        if self.is_auto_confirm:
            orders.filtered(lambda o: o.state in ('draft', 'sent')).action_confirm()
        if kw.get('no_create_self_confirm_only', False):
            return self.env['account.move']
        return orders._create_invoices(
            grouped=not (self.is_grouped_move and (len(orders) > 1)), final=True
        )

    def _action_purchase_order_move_create(self, orders, **kw):
        account_moves = self.env['account.move']

        # conditions
        confirm_forcefully = (self.is_auto_confirm and self.confirm_by == 'force')
        confirm_by_policy = (self.is_auto_confirm and self.confirm_by == 'policy')
        is_proforma = (orders[0].partner_id.invoicing_method in ('proforma', False))

        # bypass if {is_proforma == True}
        if (confirm_forcefully or (confirm_by_policy and (not is_proforma))):
            orders.button_confirm()
            if kw.get('no_create_self_confirm_only', False):
                orders.action_create_invoice()
                account_moves |= orders.invoice_ids.filtered(lambda m: m.state in ('draft', 'posted'))
        return account_moves

    # // generate move actions
    def _action_create_move(self, orders, **kw):
        return getattr(self, '_action_%s_move_create' % self.env[self.model_id.model]._table)(orders, **kw)

    def _action_create_sent_move(self, orders, **kw):
        moves = self._action_create_move(orders, **kw)
        self.action_sent_move(moves)
        return moves

    def _action_create_confirm_move(self, orders, **kw):
        moves = self._action_create_move(orders, **kw)
        # for purchase orders
        po_moves = moves.filtered(lambda move: move.is_purchase_document(include_receipts=True))
        for move in po_moves:
            move.invoice_date = fields.Date.context_today(self)
            move.with_context(check_move_validity=False)._onchange_invoice_date()
        moves.action_post()
        return moves

    def _action_create_confirm_sent_move(self, orders, **kw):
        moves = self._action_create_confirm_move(orders, **kw)
        self.action_sent_move(moves)
        return moves


    # // workflow actions
    def _process(self, partner_id, orders, **kw):
        action = kw.get('action', '')
        if not action:
            action = '_action_%s_move' % self.move_confirmation

        Model = self.env[self.model_id.model]
        if not orders:
            return False
        if self.partner_with_threshold and orders._check_is_partner_wo_invoicing_threshold(partner_id):
            return False

        logs = list()
        AccountMoves = self.env['account.move']
        if self.is_grouped_move:
            try:
                AccountMoves = getattr(self, action)(orders, **kw)
                logs = [dict(
                        name=partner_id.display_name,
                        message=_("%d %s(s) generated for %d orders.") % (
                                len(AccountMoves), self._get_move_string(), len(orders),
                            ),
                        self_log=True,
                    )]
            except (UserError, ValidationError) as err:
                logs = [dict(name=' | '.join(orders.mapped('name')), message=err)]
        else:
            move_count = 0
            for order in orders:
                try:
                    AccountMoves |= getattr(self, action)(order, **kw)
                    move_count += len(AccountMoves)
                except (UserError, ValidationError) as err:
                    logs += [dict(name=order.display_name, message=err)]
            if move_count:
                logs += [dict(
                        name=partner_id.display_name,
                        message=_("%d orders processed and %d %s(s) created.") % (
                                len(orders), len(AccountMoves), self._get_move_string()
                            ),
                        self_log=True,
                    )]
        # log if needed
        if kw.get('no_logs', False) == False:
            self._handle_logs(partner_id, logs)
        return True

    def button_process(self):
        self.ensure_one()
        Model = self.env[self.model_id.model]
        orders = Model.search(self._parse_domain())
        action = '_action_%s_move' % self.move_confirmation

        if not hasattr(self, action):
            # handle {{NotImplementedError}} in case of future need
            return False

        for partner_id, order_ids in groupby(orders, key=lambda o: o[self._get_partner_field()]):
            grouped_orders = Model.concat(*order_ids)
            self._process(partner_id, grouped_orders, action=action)
            # if not grouped_orders:
            #     continue
            # if self.partner_with_threshold and grouped_orders._check_is_partner_wo_invoicing_threshold(partner_id):
            #     continue

            # logs = list()
            # if self.is_grouped_move:
            #     try:
            #         getattr(self, action)(grouped_orders)
            #     except (UserError, ValidationError) as err:
            #         logs += [dict(name=' | '.join(grouped_orders.mapped('name')), message=err)]
            # else:
            #     for order in grouped_orders:
            #         try:
            #             getattr(self, action)(order)
            #         except (UserError, ValidationError) as err:
            #             logs += [dict(name=order.display_name, message=err)]
            # self._handle_logs(partner_id, logs)
        self.button_processed()
        return False


    def button_process_json(self, **kw):
        limit = kw.get('limit', 80)
        offset = kw.get('offset', 0)
        if (not ('prefetch' in kw)):
            offset = (offset + kw.get('limit', 80))

        Model = self.env[self.model_id.model]
        domain = self._parse_domain() + [
            (self._get_partner_field(), "not in", self.processed_partner_ids.ids)
        ]

        current_partner_id = kw.get('partner', dict()).get('id', 0)
        next_possible_partner = lambda: Model.search(
                domain, order='partner_id'
            ).mapped('partner_id')[:1]

        if not current_partner_id:
            current_partner_id = next_possible_partner().id

        if current_partner_id and (current_partner_id in self.processed_partner_ids.ids):
            domain += [(self._get_partner_field(), "=", next_possible_partner().id)]

        if current_partner_id and (current_partner_id not in self.processed_partner_ids.ids):
            domain += [(self._get_partner_field(), "=", current_partner_id)]

        orders = Model.search(domain, order='partner_id')
        orders_count = len(orders)
        partners = orders.mapped('partner_id')
        partner = orders.mapped('partner_id')[:1]

        # update offset before processing orders
        offset = 0 if ((partner and partner.id or 0) != current_partner_id) else offset

        remain_orders_count = len(orders[offset:])
        if partner:
            orders_to_process = orders[offset:(limit + offset)]
            # if `is_grouped_move` is True
            # process orders only for confirm
            # invoice should be created once orders processed
            self._process(
                    partner,
                    orders_to_process,
                    no_create_self_confirm_only=self.is_grouped_move,
                    no_logs=True,
                )
            if remain_orders_count < 80:
                # `_process` for grouped moves to create grouped invoice
                if self.is_grouped_move:
                    self._process(
                            partner,
                            orders,
                            no_create_self_confirm_only=False,
                        )
                self.processed_partner_ids = [(4, partner.id)]
        else:
            self.button_processed()

        return dict(
            orders_count=orders_count,
            processed_orders_count=orders_count if (orders_count <= 80) else (orders_count - remain_orders_count),
            partner_str=self._get_partner_string(),
            partner_count=self.partner_count,
            processed_partner_count=len(self.processed_partner_ids),
            partner=partner and partner.read(['name', 'id'])[0] or dict(),
            limit=kw.get('limit', 80),
            offset=offset,
        )

    def button_processed(self):
        self.ensure_one()
        self.write({'state': "processed"})

    def button_start(self):
        self.ensure_one()
        self.write({
            'state': "start",
            'processed_partner_ids': [(5, 0, 0)],
        })

    def button_cancel(self):
        self.ensure_one()
        self.write({'state': "cancel"})
