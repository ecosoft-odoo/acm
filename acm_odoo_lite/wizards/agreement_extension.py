# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models, fields


class AgreementExtension(models.TransientModel):
    _inherit = "agreement.extension"

    force = fields.Boolean(
        default=True,
    )

    @api.multi
    def _unlink_new_agreement_lines(self, new_agreement):
        return
