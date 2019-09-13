# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountAnalyticAccountTerminate(models.TransientModel):
    _name = 'account.analytic.account.terminate'
    _description = 'Terminate the contract'

    date_termination = fields.Date(
        string='Termination Date',
    )
    date_breach = fields.Date(
        string='Breach Date',
    )
    breach_description = fields.Text(
        string='Breach Description',
        help='Description of the agreement',
    )
    contract_genre = fields.Selection(
        [('breach', 'Breach'),
         ('termination', 'Termination'),
         ],
        default='breach',
        required=True,
    )

    @api.multi
    def terminate_contract(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(active_id)
        if self.contract_genre == 'breach':
            agreement.date_breach = self.date_breach
            agreement.breach_description = self.breach_description
            agreement.breach_agreement = True
        else:
            agreement.date_termination = agreement.date_termination
            contract = self.env['account.analytic.account'].\
                search([('agreement_id', '=', agreement.id)])
            if contract:
                contract.active = False

    @api.multi
    def action_terminate_contract(self):
        return self.terminate_contract()
