from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccountCreate(models.TransientModel):
    _name = 'account.analytic.account.create'
    _description = 'Create contract the selected agreement'

    new_partner = fields.Many2one(
        "res.partner",
    )
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )
    reject_date = fields.Date(
        string="Reject Date",
        default=fields.Date.context_today,
    )
    violate_date = fields.Date(
        string="Violate Date",
        default=fields.Date.context_today,
    )
    transfer_date = fields.Date(
        string="Transfer Date",
        default=fields.Date.context_today,
    )
    recurring_interval = fields.Integer(
        default=1,
        string="Repeat Every",
        help="Repeat every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(
        [("daily", "Day(s)"),
         ("weekly", "Week(s)"),
         ("monthly", "Month(s)"),
         ("monthlylastday", "Month(s) last day"),
         ("yearly", "Year(s)"),
         ],
        default="monthly",
        string="Recurrence",
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
    contract_genre = fields.Selection(
        [("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default="renew",
    )

    @api.multi
    def search_agreement_id(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['account.analytic.account'].browse(active_id)
        return agreement.agreement_id

    @api.multi
    def change_agreement_date(self):
        agreement = self.search_agreement_id()
        if self.start_date:
            agreement.start_date = self.start_date
        if self.end_date:
            agreement.end_date = self.end_date

    @api.multi
    def create_contract(self):
        self.ensure_one()
        agreement = self.search_agreement_id()
        old_contract = self.env['account.analytic.account'].\
            search([('agreement_id', '=', agreement.id)])
        if len(old_contract) != 1:
            raise ValidationError(
                _('%s Contract are active.') % len(old_contract)
            )
        agreement.contract_genre = self.contract_genre
        if self.contract_genre == 'renew':
            self.change_agreement_date()
            agreement.is_contract_create = False
            contract = agreement.create_new_contract()
            contract._onchange_active()
            old_contract.renew_contract_id = contract.id
            contract.contract_genre = self.contract_genre
            contract.recurring_interval = self.recurring_interval
            contract.recurring_rule_type = self.recurring_rule_type
        else:
            old_contract.active = False
            contract = agreement.create_new_contract()
            if self.contract_genre == 'reject':
                contract.reject_date = self.reject_date
            elif self.contract_genre == 'violate':
                contract.violate_date = self.violate_date
                contract.description = self.description
            contract.active = False
            contract.date_start = old_contract.date_start
            contract.date_end = old_contract.date_end
            contract.recurring_next_date = old_contract.recurring_next_date
            contract.contract_genre = self.contract_genre
            if self.contract_genre == 'transfer':
                old_agreement_line = self.env['agreement.line'].\
                    search([('agreement_id', '=', agreement.id)])
                new_agreement = agreement.create_new_agreement()
                new_agreement = self.env['agreement'].\
                    browse(new_agreement['res_id'])
                new_agreement.name = agreement.name + " - Transfer"
                new_agreement.partner_id = self.new_partner
                agreement.transfer_agreement_id = new_agreement.id
                new_agreement.transfer_agreement_id = agreement.id
                new_agreement.contract_genre = 'new'
                for line in old_agreement_line:
                    line = line.copy(
                        default={'agreement_id': new_agreement.id}
                    )
                new_contract = new_agreement.create_new_contract()
                new_recurring_interval = old_contract.recurring_interval
                new_recurring_rule_type = old_contract.recurring_rule_type
                new_contract.recurring_interval = new_recurring_interval
                new_contract.recurring_rule_type = new_recurring_rule_type

    @api.multi
    def action_create_contract(self):
        return self.create_contract()
