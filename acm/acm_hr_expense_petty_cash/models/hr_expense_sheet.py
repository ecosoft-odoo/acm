# Copyright 20 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def _default_petty_cash_journal_id(self):
        return self.env['account.journal'].search([
            ('type', '=', 'purchase')], limit=1)

    petty_cash_journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        states={'done': [('readonly', True)], 'post': [('readonly', True)]},
        default=_default_petty_cash_journal_id,
    )
