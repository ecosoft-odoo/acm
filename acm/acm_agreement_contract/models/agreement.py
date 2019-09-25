# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Supplier Contract'),
        ],
        default='sale',
        required=True,
    )
    is_contract_create = fields.Boolean(
        compute='_compute_is_contract_create'
    )
    contract_ids = fields.One2many(
        'account.analytic.account',
        'agreement_id',
        context={'active_test': False},
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
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
        required=True,
        help='Specify Interval for automatic invoice generation.',
    )
    date_contract = fields.Date(
        string='Contract Date',
    )

    @api.multi
    @api.depends('contract_ids', 'contract_ids.active')
    def _compute_is_contract_create(self):
        for agreement in self:
            contracts = agreement.contract_ids
            active_contract = contracts.filtered(lambda l: l.active is True)
            if active_contract:
                agreement.is_contract_create = True

    @api.multi
    def action_view_contract(self):
        """
        Action view, If agreement have only 1 contract will action form view
        but if agreement have more 1 contract will action list view
        """
        self.ensure_one()
        if not self.contract_ids:
            raise UserError(_('Please create contract.'))
        action_id = 'contract.action_account_analytic_%s_overdue_all' \
            % (self.contract_type, )
        action = self.env.ref(action_id).read()[0]
        action.update({
            'context': {'active_test': False},
            'domain': [('id', 'in', self.contract_ids.ids)],
        })
        if len(self.contract_ids) == 1:
            view_id = 'contract.account_analytic_account_%s_form' \
                % (self.contract_type, )
            action.update({
                'views': [(self.env.ref(view_id).id, 'form')],
                'res_id': self.contract_ids[0].id,
            })
        return action

    @api.multi
    def prepare_contract(self):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id),
             ], limit=1
        )
        vals = ({
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
        })
        return vals

    @api.multi
    def prepare_contract_line(self, line):
        val = {
            'product_id': line.product_id.id,
            'name': line.name,
            'quantity': line.qty,
            'uom_id': line.uom_id.id,
            'price_unit': line.product_id.lst_price,
        }
        return val

    @api.multi
    def create_child_contract(self):
        child_agreement = self.env['agreement'].search(
            [('parent_agreement_id', '=', self.id)])
        parent_contract = self.env['account.analytic.account'].search(
            [('agreement_id', '=', self.id)]
        )
        for contract in child_agreement:
            val = contract.prepare_contract()
            val.update({'parent_contract_id': parent_contract.id})
            contract = contract.env['account.analytic.account'].create(val)
            vals = []
            # In case child agreemnt have more 1 product
            for rec in contract.agreement_id:
                for lines in rec.line_ids:
                    new_line = rec.prepare_contract_line(lines)
                    vals.append((0, 0, new_line))
                contract.write({'recurring_invoice_line_ids': vals})
                vals = []
        return contract

    @api.multi
    def create_new_contract(self):
        self.ensure_one()
        if self.is_contract_create:
            raise UserError(_('Contract is still active.'))
        val = self.prepare_contract()
        contract = self.env['account.analytic.account'].create(val)
        vals = []
        for line in self.line_ids:
            new_line = self.prepare_contract_line(line)
            vals.append((0, 0, new_line))
        contract.write({'recurring_invoice_line_ids': vals})
        self.create_child_contract()
        return contract
