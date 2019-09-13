# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementContractCreate(models.TransientModel):
    _inherit = 'agreement.contract.create'
    _description = 'Create contract the selected agreement'

    new_partner = fields.Many2one(
        'res.partner',
        string='New Partner',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        help='Repeat every (Days/Week/Month/Year)',
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        string='Recurrence',
        default='monthly',
        help='Specify Interval for automatic invoice generation.',
    )
    contract_genre = fields.Selection(
        [('lease', 'Lease Contract'),
         ('extension', 'Extension Contract'),
         ('transfer', 'Transfer Contract'),
         ],
        default='lease',
    )

    @api.multi
    def create_contract(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(active_id)
        if agreement.is_contract_create == 'False':
            raise UserError(_('Please create contract.'))
        if self.contract_genre == 'extension':
            val = {
                'name': agreement.name + ' - Extension 1',
                'extension_agreement_id': agreement.id,
                'transfer_agreement_id': [],
                'start_date': self.date_start,
                'end_date': self.date_end,
                'recurring_interval': self.recurring_interval,
                'recurring_rule_type': self.recurring_rule_type,
            }
            new_agreement = agreement.copy(default=val)
            contract = new_agreement.create_new_contract()
            contract.active = False
            return new_agreement.action_view_contract()
        elif self.contract_genre == 'transfer':
            val = {
                'name': agreement.name + ' - Transfer 1',
                'extension_agreement_id': [],
                'transfer_agreement_id': agreement.id,
                'partner_id': self.new_partner.id,
                'start_date': self.date_start,
                'end_date': self.date_end,
                'recurring_interval': self.recurring_interval,
                'recurring_rule_type': self.recurring_rule_type,
            }
            new_agreement = agreement.copy(default=val)

    @api.multi
    def action_create_contract(self):
        if self.contract_genre == 'extension':
            return self.create_contract()
        elif self.contract_genre == 'transfer':
            return self.create_contract()
        else:
            return super().action_create_contract()
