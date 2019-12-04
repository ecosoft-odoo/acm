# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    type2 = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('utility', 'Utility'),
            ('toilet', 'Toilet'),
            ('others', 'Others'),
        ],
        string='Invoice Type',
    )
    groups = fields.Char(
        compute='_compute_groups',
        string='Zone',
        store=True,
    )

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_groups(self):
        for rec in self:
            groups = list(set(rec.invoice_line_ids.mapped('group_id.name')))
            groups.sort()
            rec.groups = ', '.join(groups)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='account_analytic_id.group_id',
        string='Zone',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='analytic_account_id.group_id',
        string='Zone',
    )
