# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountAnalyticContract(models.Model):
    _inherit = 'account.analytic.contract'

    agreement_id = fields.Many2one(
        string='Agreement',
        comodel_name='agreement',
        ondelete='restrict',
        readonly=True,
    )

    @api.multi
    @api.constrains('active')
    def _check_active(self):
        self.ensure_one()
        # Active contract must have only one
        self = self.with_context(active_test=True)
        contracts = self.search([('agreement_id', '=', self.agreement_id.id)])
        if len(contracts) > 1:
            raise UserError(_('There is some contract active already.'))
