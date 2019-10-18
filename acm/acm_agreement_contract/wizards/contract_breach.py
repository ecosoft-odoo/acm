# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractBreach(models.TransientModel):
    _name = 'contract.breach'

    date_breach = fields.Date(
        string='Breach Date',
        default=fields.Date.today(),
    )
    reason_breach = fields.Text(
        string='Breach Reason',
    )

    @api.multi
    def action_breach_contract(self):
        context = self._context.copy()
        agreement_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(agreement_id)
        if agreement.state != 'active':
            raise UserError(_('Agreement is not active.'))
        if agreement.is_contract_create is False:
            raise UserError(_('Contract is not active.'))
        if self.date_breach > fields.Date.today():
            raise UserError(_('Breach Date cannot more than Current Date'))
        agreement.write({
            'is_breach': True,
            'date_breach': self.date_breach,
            'reason_breach': self.reason_breach,
        })
        return agreement
