# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AgreementTransfer(models.TransientModel):
    _inherit = 'agreement.transfer'

    @api.multi
    def _unlink_new_agreement_lines(self, new_agreement):
        return
