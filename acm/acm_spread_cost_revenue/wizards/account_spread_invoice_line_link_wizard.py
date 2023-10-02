# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountSpreadInvoiceLineLinkWizard(models.TransientModel):
    _inherit = 'account.spread.invoice.line.link.wizard'

    @api.multi
    def confirm(self):
        self.ensure_one()
        context = self._context.copy()
        # Pass invoice_line_id in context for use in function _prepare_spread_from_template
        context['invoice_line_id'] = self.invoice_line_id.id
        self = self.with_context(context)
        return super().confirm()
