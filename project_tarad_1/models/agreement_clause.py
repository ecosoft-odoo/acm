# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AgreementClause(models.Model):
    _inherit = "agreement.clause"

    contract_create_type = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default="new",
    )
