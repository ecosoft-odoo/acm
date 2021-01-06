# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementInActive(models.TransientModel):
    _name = 'agreement.inactive'
    _description = 'Inactive Agreement'

    inactive_reason = fields.Selection(
        selection=lambda self: self._get_selection_inactive_reason(),
        string='Inactive Reason',
        required=True,
    )

    @api.model
    def _get_selection_inactive_reason(self):
        agreement_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(agreement_ids)
        selection = [
            ('cancel', 'Cancelled'),
            ('expire', 'Expired'), ]
        try:
            if len(agreements) == 1:
                if agreements[0].is_transfer:
                    selection = [('transfer', 'Transferred')]
                elif agreements[0].is_terminate:
                    selection = [('terminate', 'Terminated')]
        except Exception as ex:
            print(ex)
        return selection

    @api.model
    def default_get(self, fields):
        res = super(AgreementInActive, self).default_get(fields)
        agreement_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(agreement_ids)
        if len(agreements) == 1:
            if agreements[0].is_transfer:
                res['inactive_reason'] = 'transfer'
            elif agreements[0].is_terminate:
                res['inactive_reason'] = 'terminate'
        elif any(agreements.mapped('is_transfer')) or \
                any(agreements.mapped('is_terminate')):
            raise UserError(
                _('Transferred or terminated agreement '
                  'can not batch inactive agreement.'))
        return res

    @api.multi
    def action_inactive_agreement(self):
        """
        This is for manual inactive agreement.
        """
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        for agreement in agreements:
            invoice = agreement.invoice_id
            if invoice and invoice.state != 'paid':
                raise UserError(_("Vendor Bill's still open."))
            agreement.inactive_statusbar()
            agreement.inactive_reason = self.inactive_reason
        return agreements.view_agreement()
