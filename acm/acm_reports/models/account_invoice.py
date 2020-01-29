# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _description = 'Account Invoice'

    move_line_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Move Lines',
        compute='_compute_move_line_ids',
    )

    @api.multi
    def _compute_move_line_ids(self):
        for rec in self:
            payment_infos = rec._get_payments_vals()
            move_ids = list(map(lambda d: d['move_id'], payment_infos))
            move = rec.env['account.move'].browse(move_ids)
            rec.move_line_ids = move.mapped('line_ids').sorted('debit', True)

    @api.multi
    def _get_date(self, dict, lang):
        code = self.env['res.lang'].search([('code', '=', lang)])
        date_paid = ', '.join(date.strftime(code.date_format) for date in dict)
        return date_paid
