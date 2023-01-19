# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AgreementCreate(models.TransientModel):
    _inherit = "agreement.create"

    income_type_id = fields.Many2one(
        required=False,
    )
