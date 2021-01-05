# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Period',
        index=True,
        copy=False,
    )
