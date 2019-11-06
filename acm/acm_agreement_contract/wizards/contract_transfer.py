# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractTransfer(models.TransientModel):
    _name = 'contract.transfer'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='New Partner',
        required=True,
    )
    partner_contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Primary Contact',
        help='The primary partner contact (If Applicable).',
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
    )
    date_contract = fields.Date(
        string='Contract Date',
        default=fields.Date.today(),
        required=True,
    )

    @api.multi
    def action_transfer_contract(self):
        context = self._context.copy()
        Agreement = self.env['agreement']
        agreements = Agreement.browse(context.get('active_ids', []))
        new_agreements = Agreement
        for agreement in agreements:
            if agreement.is_contract_create is False:
                raise UserError(
                    _('Please create contract of %s.' % (agreement.name, )))
            agreement = agreement.with_context({
                'partner_id': self.partner_id.id,
                'partner_contact_id': self.partner_contact_id.id,
                'date_contract': self.date_contract,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'is_transfer': True,
                'transfer_agreement_id': agreement.id,
            })
            new_agreements += agreement.create_agreement()
        return new_agreements.view_agreement()
