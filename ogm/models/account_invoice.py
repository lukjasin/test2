# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2011 Noviat nv/sa (www.noviat.be). All rights reserved.

from odoo import api, fields, models

"""
account.move object: add support for Belgian structured communication
"""


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_reference_be_invoice(self):
        """ This computes the reference based on the belgian national standard
            “OGM-VCS”.
            The data of the reference is the database id number of the invoice.
            For instance, if an invoice is issued with id 654, the check number
            is 72 so the reference will be '+++000/0000/65472+++'.
        """
        self.ensure_one()
        base = int(self.name)
        bbacomm = str(base)
        mod = base % 97 or 97
        reference = '+++%s/%s/%s%01d%02d+++' % (bbacomm[0:3], bbacomm[3:7], bbacomm[7:9], 0, mod)
        return reference

