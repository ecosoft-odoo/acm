# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementBreach(models.TransientModel):
    _name = 'agreement.breach'
    _description = 'Agreement Breach'

    date_breach = fields.Date(
        string='Breach Date',
        default=fields.Date.today(),
    )
    breach_type_id = fields.Many2one(
        comodel_name='acm.breach.type',
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
    def action_breach_agreement(self):
        self.ensure_one()
        context = self._context.copy()
        agreement_ids = context.get('active_ids', [])
        agreements = self.env['agreement'].browse(agreement_ids)
        for agreement in agreements:
            agreement._validate_contract_create()
            if context.get('breach'):
                self.env['agreement.breach.line'].create({
                    'date_breach': self.date_breach,
                    'breach_type_id': self.breach_type_id.id,
                    'reason_breach': self.reason_breach,
                    'agreement_id': agreement.id,
                })
                agreement.is_breach = True
            else:
                agreement.breach_line_ids.filtered(
                    lambda l: not l.date_cancel_breach).write({
                        'date_cancel_breach': self.date_cancel_breach,
                        'reason_cancel_breach': self.reason_cancel_breach,
                    })
                agreement.is_breach = False
        return agreements
