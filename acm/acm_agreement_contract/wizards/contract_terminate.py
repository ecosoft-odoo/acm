# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractTerminate(models.TransientModel):
    _name = 'contract.terminate'
    _description = 'Terminate contract from agreement'

    date_termination = fields.Date(
        string='Termination Date',
        default=fields.Date.today(),
    )
    reason = fields.Text(
        string='Termination Reason',
    )

    @api.multi
    def action_terminate_contract(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(active_id)
        if agreement.state != 'active':
            raise UserError(_('Agreement is not active.'))
        if agreement.is_contract_create == 'False':
            raise UserError(_('Contract is not active.'))
        if self.date_termination > fields.Date.today():
            raise UserError(
                _('Termination Date cannot more than Current Date'))
        agreement.termination_date = self.date_termination
        agreement.terminate_reason = self.reason
        return agreement.inactive_statusbar()
