# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Supplier Contract'), ],
        default='sale',
        required=True,
    )
    is_contract_create = fields.Boolean(
        compute='_compute_is_contract_create',
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
        help='Repeat every (Days/Week/Month/Year)',
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('yearly', 'Year(s)'), ],
        string='Recurrence',
        default='monthly',
        required=True,
        help='Specify Interval for automatic invoice generation.',
    )
    date_contract = fields.Date(
        string='Contract Date',
    )

    @api.multi
    def search_contract(self):
        self.ensure_one()
        Contract = self.env['account.analytic.account']
        contracts = Contract.search([('agreement_id', '=', self.id)])
        return contracts

    @api.multi
    def _compute_is_contract_create(self):
        for agreement in self:
            if agreement.search_contract():
                agreement.is_contract_create = True

    @api.multi
    def get_agreement_vals(self):
        self.ensure_one()
        return {
            'name': 'NEW',
            'active': True,
            'version': 1,
            'revision': 0,
            'state': 'draft',
            'stage_id': self.env.ref('agreement_legal.agreement_stage_new').id,
            'partner_id': self._context.get('partner_id'),
            'date_contract': self._context.get('date_contract'),
            'start_date': self._context.get('start_date'),
            'end_date': self._context.get('end_date'),
            'recurring_interval': self._context.get('recurring_interval'),
            'recurring_rule_type': self._context.get('recurring_rule_type'),
            'parent_agreement_id': False,
        }

    @api.multi
    def _create_agreement(self):
        self.ensure_one()
        vals = self.get_agreement_vals()
        # Create agreement
        vals['name'] = self.name + ' - %s' % self._context.get('name')
        new_agreement = self.copy(default=vals)
        new_agreement.sections_ids.mapped('clauses_ids').write({
            'agreement_id': new_agreement.id})
        # Create child agreement
        vals['parent_agreement_id'] = new_agreement.id
        for child in self.child_agreements_ids:
            vals['name'] = child.name + ' - %s' % self._context.get('name')
            child_agreement = child.copy(default=vals)
            child_agreement.sections_ids.mapped('clauses_ids').write({
                'agreement_id': child_agreement.id})
        return {
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_agreement.id,
        }

    @api.multi
    def action_view_contract(self):
        """
        Action view, If agreement have only 1 contract will action form view
        but if agreement have more 1 contract will action list view
        """
        self.ensure_one()
        if not self.is_contract_create:
            raise UserError(_('Please create contract.'))
        action_id = 'contract.action_account_analytic_%s_overdue_all' \
            % (self.contract_type, )
        action = self.env.ref(action_id).read()[0]
        contracts = self.search_contract()
        if contracts:
            view_id = 'contract.account_analytic_account_%s_form' \
                % (self.contract_type, )
            action.update({
                'views': [(self.env.ref(view_id).id, 'form')],
                'res_id': contracts[0].id,
            })
        return action

    @api.multi
    def prepare_contract(self):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id),
             ], limit=1, )
        return {
            'name': self.name,
            'contract_type': self.contract_type,
            'agreement_id': self.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
            'recurring_invoices': True,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'recurring_next_date': self.start_date,
            'active': True,
        }

    @api.multi
    def create_new_contract(self):
        self.ensure_one()
        if self.is_contract_create:
            raise UserError(_('Contract is still active.'))
        val = self.prepare_contract()
        contract = self.env['account.analytic.account'].create(val)
        vals = []
        for line in self.line_ids:
            new_line = line.prepare_contract_line()
            vals.append((0, 0, new_line))
        contract.write({'recurring_invoice_line_ids': vals})
        # Create Child Contract
        child_agreement = self.env['agreement'].search(
            [('parent_agreement_id', '=', self.id)])
        for contract in child_agreement:
            contract.create_new_contract()
        return contract
