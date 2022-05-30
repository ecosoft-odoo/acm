# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementActive(models.TransientModel):
    _name = 'agreement.active'
    _description = 'Active Agreement'

    group_ids = fields.Many2many(
        comodel_name='account.analytic.group',
        string='Zone',
        default=lambda self: self._default_group_ids(),
        readonly=True,
    )

    @api.model
    def _get_agreements(self):
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        return agreements

    @api.model
    def _default_group_ids(self):
        agreements = self._get_agreements()
        group_ids = agreements.mapped('group_id')
        return group_ids

    @api.multi
    def action_active_agreement(self):
        self.ensure_one()
        agreements = self._get_agreements()
        agreements.active_statusbar()
        return agreements.view_agreement()
