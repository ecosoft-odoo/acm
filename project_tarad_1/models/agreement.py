# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    contract_create_type = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default="new",
    )
    sections_ids = fields.One2many(
        domain=lambda self: [
            ('contract_create_type', '=', self.contract_create_type)]
    )
    clauses_ids = fields.One2many(
        domain=lambda self: [
            ('contract_create_type', '=', self.contract_create_type)]
    )
