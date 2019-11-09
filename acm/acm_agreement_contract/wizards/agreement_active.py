# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AgreementActive(models.TransientModel):
    _name = 'agreement.active'

    @api.multi
    def active_agreement(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        agreements.active_statusbar()
