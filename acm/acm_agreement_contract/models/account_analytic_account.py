# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
        ondelete='restrict',
        readonly=True,
    )

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        if not line.is_select:
            return {}
        return super(AccountAnalyticAccount, self) \
            ._prepare_invoice_line(line, invoice_id)
