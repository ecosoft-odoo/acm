# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import calendar
from odoo import models, _
from odoo.exceptions import UserError


class AccountSpreadTemplate(models.Model):
    _inherit = 'account.spread.template'

    def is_last_day_of_month(self, date):
        """
        Function for check date is the last day of month or not
        - If last day of month, return True
        - If not last day of month, return False
        """
        day = date.day
        last_day = calendar.monthrange(date.year, date.month)[1]
        return day == last_day

    def _prepare_spread_from_template(self, spread_account_id=False):
        self.ensure_one()
        spread_vals = super()._prepare_spread_from_template(spread_account_id=spread_account_id)
        # Spread must created from the invoice
        invoice_line_id = self._context.get('invoice_line_id')
        if not invoice_line_id:
            raise UserError(_('Spread must created from the invoice.'))
        # Check invoice has contract
        invoice_line = self.env['account.invoice.line'].browse(invoice_line_id)
        contract = invoice_line.account_analytic_id
        if not contract:
            raise UserError(_('Contract is not set in the invoice, please set it before validate.'))
        # Find spread date and number of spread lines
        date_start, date_end = contract.date_start, contract.date_end
        if not date_start or not date_end:
            raise UserError(_('Contract must have start date and end date.'))
        period_number = (date_end.year - date_start.year) * 12 + (date_end.month - date_start.month) + 1
        if period_number > 1 and not self.is_last_day_of_month(date_end):
            period_number = period_number - 1
        spread_vals.update({
            'period_number': period_number,
            'force_spread_date': date_start,
        })
        return spread_vals
