# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AgreementInActive(models.TransientModel):
    _name = 'agreement.inactive'

    @api.multi
    def action_inactive_agreement(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        agreements.inactive_statusbar()
        return agreements.view_agreement()
