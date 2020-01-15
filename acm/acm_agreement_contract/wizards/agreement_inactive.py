# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementInActive(models.TransientModel):
    _name = 'agreement.inactive'
    _description = 'Inactive Agreement'

    inactive_reason = fields.Selection(
        selection=[
            ('cancel', 'Cancelled'),
            ('terminate', 'Terminated'),
            ('transfer', 'Transferred'),
            ('expire', 'Expired'),
        ],
        string='Inactive Reason',
        default='cancel',
        required=True,
    )

    @api.multi
    def action_inactive_agreement(self):
        """
        This is for manual inactive agreement.
        """
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        for agreement in agreements:
            agreement.inactive_statusbar()
            agreement.inactive_reason = 'cancel'
        return agreements.view_agreement()
