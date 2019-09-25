# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    agreement_id = fields.Many2one(
        'agreement',
        string='Agreement',
        ondelete='restrict',
        readonly=True,
    )
    parent_contract_id = fields.Many2one(
        'account.analytic.account',
        string='Parent Contract',
        ondelete='restrict',
        readonly=True,
    )

    @api.multi
    def recurring_create_invoice(self):
        child_contract = self.env['account.analytic.account'].search(
            [('parent_contract_id', '=', self.id)])
        for rec in child_contract:
            rec.recurring_create_invoice()
        return super().recurring_create_invoice()
