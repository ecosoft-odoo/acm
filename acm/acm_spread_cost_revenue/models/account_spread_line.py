# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountInvoiceSpreadLine(models.Model):
    _inherit = 'account.spread.line'
    _order = 'date, id'