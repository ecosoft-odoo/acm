# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import calendar
from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountSpreadTemplate(models.Model):
    _inherit = 'account.spread.template'

    def is_last_day_of_month(self, date):
        """
        Function for check that date is the last day of month or not
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
        # Find spread date and number of spread lines
        invoice_line = self.env['account.invoice.line'].browse(invoice_line_id)
        invoice = invoice_line.invoice_id
        contract = invoice_line.account_analytic_id
        period_number = 12  # Default period number
        spread_date = invoice.date_invoice or fields.Date.context_today(self)  # Default spread date will equal to invoice date
        if not contract:  # ACM need contract
            raise UserError(_('Analytic Account is not set in invoice, please set before validate it.'))
        if contract:
            if not contract.date_start or not contract.date_end:
                raise UserError(_('Contract must have start date and end date.'))
            # If spread date is before contract start date, spread date will equal to contract start date
            if spread_date < contract.date_start:
                spread_date = contract.date_start
            if not (contract.date_start <= spread_date <= contract.date_end):
                raise UserError(_('Spread date must to be in period of contract.'))
            # Period number
            period_number = (contract.date_end.year - spread_date.year) * 12 + (contract.date_end.month - spread_date.month) + 1
            if period_number > 1 and not self.is_last_day_of_month(contract.date_end):
                period_number = period_number - 1
        spread_vals.update({
            'period_number': period_number,
            'force_spread_date': spread_date,
        })
        return spread_vals
