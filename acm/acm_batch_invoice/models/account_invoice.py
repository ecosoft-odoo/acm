# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    meter_from = fields.Float(
        string='Meter From',
        digits=(12, 0),
    )
    meter_to = fields.Float(
        string='Meter To',
        digits=(12, 0),
    )

    @api.onchange('meter_from', 'meter_to')
    def _onchange_meter_from_to(self):
        if self.invoice_id.type2 == 'utility':
            self.quantity = self.meter_to - self.meter_from
