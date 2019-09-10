# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class Agreement(models.Model):
    _inherit = "agreement"

    contract_genre = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default="new",
    )
    transfer_agreement_id = fields.Many2one(
        "agreement",
        string="Agreement",
        readonly=True,
    )
    contract_genre_id = fields.Many2one(
        "agreement.genre",
    )
