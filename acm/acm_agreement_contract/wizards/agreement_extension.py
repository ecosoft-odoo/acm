# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class AgreementExtension(models.TransientModel):
    _name = 'agreement.extension'
    _description = 'Extension Agreement'

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
    force = fields.Boolean()

    @api.multi
    def action_extension_agreement(self):
        context = self._context.copy()
        Agreement = self.env['agreement']
        agreements = Agreement.browse(context.get('active_ids', []))
        new_agreements = Agreement
        # Do not allow to renew agreement, when working with force
        if self.force and len(agreements) > 1:
            raise UserError(
                _('Renew agreement not allowed when working in batch.'))
        for agreement in agreements:
            # Contract must to created
            if not agreement.is_contract_create:
                raise UserError(
                    _('Please create contract %s.' % (agreement.name, )))
            # Agreement period must valid
            if agreement.end_date >= self.date_start:
                raise UserError(
                    _('%s is still active on the date you selected.')
                    % (agreement.name, ))
            if not self.force:
                # Agreement period must valid
                time = relativedelta(
                    agreement.end_date, agreement.start_date - timedelta(1))
                new_start_date = agreement.start_date + time
                new_end_date = agreement.end_date + time
                if new_start_date != self.date_start or \
                   new_end_date != self.date_end:
                    raise UserError(
                        _('Invalid agreement period of %s.') % (
                            agreement.display_name, ))
            # Create Agreement
            agreement = agreement.with_context({
                'partner_id': agreement.partner_id.id,
                'partner_contact_id': agreement.partner_contact_id.id,
                'date_contract': self.date_contract,
                'date_start': self.date_start,
                'date_end': self.date_end,
            })
            new_agreement = agreement.create_agreement()
            if not self.force:
                # Compute Start Date and End Date in Products/Services
                new_agreement._compute_line_start_end_date(time)
            new_agreements |= new_agreement
        return new_agreements.view_agreement()
