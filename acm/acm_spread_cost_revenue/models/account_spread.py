# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import datetime
from odoo import api, models, fields


class AccountSpread(models.Model):
    _inherit = 'account.spread'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        related='invoice_line_id.group_id',
        store=True,
        readonly=True,
    )
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract',
        related='invoice_line_id.account_analytic_id',
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Lessee',
        related='invoice_line_id.account_analytic_id.partner_id',
        store=True,
        readonly=True,
    )
    date_start = fields.Date(
        string='Start Date',
        related='invoice_line_id.account_analytic_id.date_start',
        store=True,
        readonly=True,
    )
    date_end = fields.Date(
        string='End Date',
        related='invoice_line_id.account_analytic_id.date_end',
        store=True,
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        related='invoice_line_id.invoice_id',
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive')],
        string='Status',
        related='invoice_line_id.account_analytic_id.agreement_id.state',
        store=True,
        readonly=True,
    )

    def create(self, vals):
        # Overwrite spread date
        if vals.get('force_spread_date'):
            vals['spread_date'] = vals['force_spread_date']
            del vals['force_spread_date']
        return super().create(vals)

    @api.multi
    def _get_number_of_periods(self, month_day):
        # Overwrite function
        self.ensure_one()
        return self.period_number

    @api.multi
    def _compute_spread_board(self):
        self.ensure_one()
        super()._compute_spread_board()
        contract = self.invoice_line_id.account_analytic_id
        if contract:
            # If found contract, let recompute amount (Only ACM)
            total_amount = self.total_amount
            start_date = self.spread_date
            end_date = contract.date_end
            amount_per_day = total_amount / ((end_date - start_date).days + 1)
            unposted_amount = total_amount
            spread_lines = self.env['account.spread.line'].search([('spread_id', "=", self.id)], order='date, id')
            for index, spread_line in enumerate(spread_lines):
                # if found account move and state = 'post', continue it
                if spread_line.move_id.state == 'posted':
                    unposted_amount -= spread_line.amount
                    continue
                # Calculate amount
                if index + 1 == 1:
                    amount = amount_per_day * ((spread_line.date - self.spread_date).days + 1)
                elif index + 1 == self.period_number:
                    amount = unposted_amount
                else:
                    amount = amount_per_day * ((spread_line.date - (spread_lines[index - 1].date + datetime.timedelta(days=1))).days + 1)
                amount = self.currency_id.round(amount)
                unposted_amount -= amount
                spread_line.write({
                    'amount': amount,
                })
