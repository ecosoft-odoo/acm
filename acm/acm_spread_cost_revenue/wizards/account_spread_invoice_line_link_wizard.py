# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountSpreadInvoiceLineLinkWizard(models.TransientModel):
    _inherit = 'account.spread.invoice.line.link.wizard'

    def confirm(self):
        self.ensure_one()
        # Spread over contract start - end date, we need to pass analytic
        ctx = self._context.copy()
        ctx.update({
            'spread_over': 'contract',  # For ACM only
            'account_analytic_id': self.invoice_line_id.account_analytic_id.id,
        })
        self = self.with_context(ctx)
        return super().confirm()
