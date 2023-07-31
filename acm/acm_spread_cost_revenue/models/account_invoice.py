# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        res = super().action_cancel()
        # Unlink spread
        invoice_lines = self.mapped('invoice_line_ids')
        spreads = invoice_lines.mapped('spread_id')
        invoice_lines.write({
            'spread_id': False,
        })
        spreads.unlink()
        return res
