# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    income_type_id = fields.Many2one(
        required=False,
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ("monthly", "Month(s)"),
            ("yearly", "Year(s)"),
        ],
    )
