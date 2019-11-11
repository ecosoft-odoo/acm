# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementTerminate(models.TransientModel):
    _name = 'agreement.terminate'

    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
        default='lessee',
        required=True,
    )
    date_termination_requested = fields.Date(
        string='Termination Requested Date',
        required=True,
    )
    date_termination = fields.Date(
        string='Termination Date',
        required=True,
    )
    reason_termination = fields.Text(
        string='Termination Reason',
        required=True,
    )

    @api.multi
    def action_terminate_agreement(self):
        self.ensure_one()
        context = self._context.copy()
        agreement_ids = context.get('active_ids', [])
        agreements = self.env['agreement'].browse(agreement_ids)
        for agreement in agreements:
            if agreement.state != 'active':
                raise UserError(_('Agreement is not active.'))
            if not agreement.is_contract_create:
                raise UserError(_('Contract is not active.'))
            agreement.write({
                'is_termination': True,
                'termination_by': self.termination_by,
                'termination_requested': self.date_termination_requested,
                'termination_date': self.date_termination,
                'reason_termination': self.reason_termination,
            })
        return agreements
