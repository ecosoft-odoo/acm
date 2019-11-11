# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AgreementCreateContract(models.TransientModel):
    _name = 'agreement.create.contract'

    @api.multi
    def action_create_contract(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        agreements.create_new_contract()
        return agreements.action_view_contract()
