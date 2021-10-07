# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MassAccountMoveSchedule(models.TransientModel):
    _name = 'mass.account.move.schedule'
    _description = 'Mass Account Move Scheduling'

    schedule_date = fields.Datetime(string='Scheduled Date')

    @api.constrains('schedule_date')
    def _check_schedule_date(self):
        for scheduler in self.filtered(lambda s: s.schedule_date < fields.Datetime.now()):
            raise ValidationError(_("Select a date equal or greater than the current date."))

    def action_schedule(self):
        active_id = self._context.get('active_id', False)
        if not active_id:
            return False
        return self.env['mass.account.move'].browse(active_id).write({
                'schedule_date': self.schedule_date,
                'state': 'scheduled'
            })
