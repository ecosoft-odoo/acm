# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, _
from odoo.exceptions import UserError


class AccountSpreadInvoiceLineLinkWizard(models.TransientModel):
    _inherit = 'account.spread.invoice.line.link.wizard'

    def confirm(self):
        self.ensure_one()
        context = self._context.copy()
        # Prevent user click create spread on invoice line
        if not context.get('allow_create_spread'):
            raise UserError(_('Do not allow create spread from invoice line directly.'))
        # Pass invoice_line_id in context for use in function _prepare_spread_from_template, To Find spread date and number of spread lines
        context['invoice_line_id'] = self.invoice_line_id.id
        self = self.with_context(context)
        return super().confirm()
