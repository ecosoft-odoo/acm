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
        next_date = line.analytic_account_id.recurring_next_date
        if not (line.date_start or line.date_end):
            return {}
        if line.date_start and not line.date_end and \
           line.date_start > next_date:
            return {}
        if line.date_end and not line.date_start and next_date > line.date_end:
            return {}
        if not(line.date_start <= next_date <= line.date_end):
            return {}
        return super(AccountAnalyticAccount, self) \
            ._prepare_invoice_line(line, invoice_id)

    @api.multi
    def recurring_create_invoice(self):
        """Create invoice only if Invoice contain some lines."""
        invoices = super().recurring_create_invoice()
        no_line_invs = invoices.filtered(lambda inv: not inv.invoice_line_ids)
        invoices -= no_line_invs
        no_line_invs.unlink()
        return invoices
