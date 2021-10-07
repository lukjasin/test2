# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MassAccountMoveHistory(models.Model):
    _name = 'mass.account.move.history'
    _description = "Mass Account Move History"

    # @api.model
    # def _selection_target_model(self):
    #     return [(model.model, model.name) for model in self.env['ir.model'].search(
    #             [('model', 'in', ['sale.order', 'purchase.order'])]
    #         )]

    # name = fields.Reference(string='Record', selection='_selection_target_model')
    name = fields.Char(string='Source Document(s)')
    message = fields.Text(string="Error Message")
    record_status = fields.Selection([
        ('pass', "Pass"),
        ('fail', "Fail"),
    ], string="Record Status", copy=False, required=True)
    mass_account_move_id = fields.Many2one(comodel_name='mass.account.move', string="Mass Account Move", copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner", copy=False)
