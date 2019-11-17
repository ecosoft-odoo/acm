# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def amount_text(self, amount):
        try:
            return num2words(amount, to='currency', lang='th')
        except NotImplementedError:
            return num2words(amount, to='currency', lang='en')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    meter_from = fields.Char()
    meter_to = fields.Char()
