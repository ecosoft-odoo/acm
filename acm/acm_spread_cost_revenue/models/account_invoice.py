# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        invoice_lines = self.mapped('invoice_line_ids')
        spreads = invoice_lines.mapped('spread_id')
        invoice_lines.write({'spread_id': False})
        for spread in spreads:
            spread.action_undo_spread()
            spread.unlink()
        return super().action_cancel()

    @api.multi
    def action_invoice_cancel(self):
        cancel_reversal = all(self.mapped('journal_id.is_cancel_reversal'))
        states = self.mapped('state')
        if cancel_reversal and 'draft' not in states:
            if all(st == 'open' for st in states) and self.mapped('invoice_line_ids.spread_id.line_ids.move_id'):
                return self.reverse_document_wizard()
        return super().action_invoice_cancel()

    @api.multi
    def action_document_reversal(self, date=None, journal_id=None):
        invoice_lines = self.mapped('invoice_line_ids')
        spreads = invoice_lines.mapped('spread_id')
        invoice_lines.write({'spread_id': False})
        for spread in spreads:
            spread.with_context(date_reversal=date).action_undo_spread()
            spread.unlink()
        return super().action_document_reversal(date=date, journal_id=journal_id)
