from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class ContractCreate(models.TransientModel):
    _name = 'contract.create'
    _description = 'Create contract the selected agreement'

    name = fields.Char(
        string='Name',
    )
    new_partner = fields.Many2one(
        'res.partner'
    )
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )
    cancel_date = fields.Date(
        string="Cancel Date",
    )
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
    )
    description = fields.Text(
        string="Description",
        help="Description of the agreement",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=False,
        copy=True,
        help="The customer or vendor this agreement is related to.",
    )
    contract_create_type = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default="new",
    )

    @api.multi
    def agreement_id(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(active_id)
        return agreement

    @api.multi
    def agreement_date(self):
        agreement = self.agreement_id()
        if self.start_date:
            agreement.start_date = self.start_date
        if self.end_date:
            agreement.end_date = self.end_date

    @api.multi
    def new_contract(self):
        self.ensure_one()
        self.agreement_date()
        agreement = self.agreement_id()
        contract = agreement.create_new_contract()
        contract.contract_create_type = self.contract_create_type
        contract.recurring_interval = self.recurring_interval
        contract.recurring_rule_type = self.recurring_rule_type
        if str(contract.date_start) >= datetime.today().strftime('%Y-%m-%d'):
            contract.active = False
        else:
            contract.active = True
        return contract

    @api.multi
    def renew_contract(self):
        self.ensure_one()
        self.agreement_date()
        agreement = self.agreement_id()
        agreement.contract_create_type = self.contract_create_type
        agreement.contract_count = 0
        contract = agreement.create_new_contract()
        contract.contract_create_type = self.contract_create_type
        contract.date_start = self.start_date
        contract.date_end = self.end_date
        contract.recurring_interval = self.recurring_interval
        contract.recurring_rule_type = self.recurring_rule_type
        if str(contract.date_start) >= datetime.today().strftime('%Y-%m-%d'):
            contract.active = False
        else:
            contract.active = True
        return contract

    @api.multi
    def reject_contract(self):
        self.ensure_one()
        agreement = self.agreement_id()
        agreement.contract_create_type = self.contract_create_type
        contract = self.env['account.analytic.account'].\
            search([('agreement_id', '=', agreement.id)])
        contract.active = False
        contract.cancel_date = self.cancel_date
        contract.contract_create_type = self.contract_create_type

    @api.multi
    def violatet_contract(self):
        self.ensure_one()
        agreement = self.agreement_id()
        agreement.contract_create_type = self.contract_create_type
        contract = self.env['account.analytic.account'].\
            search([('agreement_id', '=', agreement.id)])
        contract.active = False
        contract.cancel_date = self.cancel_date
        contract.description = self.description
        contract.contract_create_type = self.contract_create_type

    @api.multi
    def transfer_contract(self):
        self.ensure_one()
        agreement = self.agreement_id()
        agreement.contract_create_type = self.contract_create_type
        old_contract = self.env['account.analytic.account'].\
            search([('agreement_id', '=', agreement.id)])
        old_contract.active = False
        # agreement_line = self.env['agreement.line'].\
        #     search([('agreement_id', '=', agreement.id)])
        agreement = agreement.create_new_agreement()
        new_agreement = self.env['agreement'].browse(agreement['res_id'])
        new_agreement.name = self.name
        new_agreement.partner_id = self.new_partner
        self.agreement_date()
        contract = new_agreement.create_new_contract()
        contract.contract_create_type = self.contract_create_type
        contract.partner_id = self.new_partner
        contract.recurring_interval = self.recurring_interval
        contract.recurring_rule_type = self.recurring_rule_type
        return contract

    @api.multi
    def action_create_contract(self):
        if self.contract_create_type == 'new':
            return self.new_contract()
        elif self.contract_create_type == 'renew':
            return self.renew_contract()
        elif self.contract_create_type == 'reject':
            return self.reject_contract()
        elif self.contract_create_type == 'violate':
            return self.violatet_contract()
        else:
            return self.transfer_contract()
