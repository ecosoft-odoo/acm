# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


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
        """ Usually, spread will use invoice date,
        but for ACM case, we also enforce using contract start date """
        if vals.get('force_spread_date'):
            vals['spread_date'] = vals['force_spread_date']
            del vals['force_spread_date']
        return super().create(vals)
