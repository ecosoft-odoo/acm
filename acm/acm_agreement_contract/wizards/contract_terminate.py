# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractTerminate(models.TransientModel):
    _name = 'contract.terminate'

    date_termination_requested = fields.Date(
        string='Termination Requested Date',
    )
    date_termination = fields.Date(
        string='Termination Date',
    )
    reason_termination = fields.Text(
        string='Termination Reason',
    )

    @api.multi
    def action_terminate_contract(self):
        self.ensure_one()
        context = self._context.copy()
        agreement_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(agreement_id)
        if agreement.state != 'active':
            raise UserError(_('Agreement is not active.'))
        if agreement.is_contract_create is False:
            raise UserError(_('Contract is not active.'))
        # if self.date_termination > fields.Date.today():
        #     raise UserError(
        #         _('Termination Date cannot more than Current Date'))
        agreement.write({
            'is_termination': True,
            'termination_requested': self.date_termination_requested,
            'termination_date': self.date_termination,
            'reason_termination': self.reason_termination,
        })
        # agreement.inactive_statusbar()
        return agreement
