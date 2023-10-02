# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class AccountInvoiceSpreadLine(models.Model):
    _inherit = 'account.spread.line'
    _order = 'date, id'

    @api.multi
    def unlink_move(self):
        for line in self:
            move = line.move_id
            if move.journal_id.is_cancel_reversal:
                date_reversal = self._context.get('date_reversal', fields.Date.context_today(self))
                move.line_ids.remove_move_reconcile()
                move.reverse_moves(date_reversal, move.journal_id)
                line.move_id = False
            else:
                super(AccountInvoiceSpreadLine, line).unlink_move()

    @api.multi
    def _prepare_move(self):
        move_vals = super()._prepare_move()
        move_vals.pop('name')
        return move_vals
