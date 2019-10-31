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
    type_breach = fields.Char(
        string='Breach Type',
    )
    reason_breach = fields.Text(
        string='Breach Reason',
    )
    date_cancel_breach = fields.Date(
        string='Cancel Breach Date',
        default=fields.Date.today(),
    )
    reason_cancel_breach = fields.Text(
        string='Cancel Breach Reason',
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
        # Create agreement breach
        if context.get('type') == 'breach':
            self.env['agreement.breach'].create({
                'date_breach': self.date_breach,
                'type_breach': self.type_breach,
                'reason_breach': self.reason_breach,
                'agreement_id': agreement.id, })
            agreement.is_breach = True
        else:
            agreement.breach_ids.filtered(
                lambda l: l.date_cancel_breach is False).write({
                    'date_cancel_breach': self.date_cancel_breach,
                    'reason_cancel_breach': self.reason_cancel_breach,
                })
            agreement.is_breach = False
        return agreement
