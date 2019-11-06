# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractExtension(models.TransientModel):
    _name = 'contract.extension'

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
    def action_extension_contract(self):
        context = self._context.copy()
        Agreement = self.env['agreement']
        agreements = Agreement.browse(context.get('active_ids', []))
        new_agreements = Agreement
        for agreement in agreements:
            if agreement.is_contract_create is False:
                raise UserError(
                    _('Please create contract of %s.' % (agreement.name, )))
            if agreement.end_date >= self.date_start:
                raise UserError(
                    _('%s is still active on the date you selected.')
                    % (agreement.name, ))
            agreement = agreement.with_context({
                'partner_id': agreement.partner_id.id,
                'partner_contact_id': agreement.partner_contact_id.id,
                'date_contract': self.date_contract,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'is_extension': True,
                'extension_agreement_id': agreement.id,
            })
            new_agreements += agreement.create_agreement()
        return new_agreements.view_agreement()
