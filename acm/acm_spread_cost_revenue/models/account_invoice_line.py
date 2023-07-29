# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def create_auto_spread(self):
        context = self._context.copy()
        context['allow_create_spread'] = True
        self = self.with_context(context)
        super().create_auto_spread()
