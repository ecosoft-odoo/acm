# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer'),
            ('purchase', 'Supplier'),
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
    date_start = fields.Date(
        compute='_compute_start_end_date',
    )
    date_end = fields.Date(
        compute='_compute_start_end_date',
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
    def get_active_contracts(self):
        return
        # self.ensure_one()
        # contracts = self.contract_ids
        # active_contracts = contracts.filtered(lambda l: l.active is True)
        # return active_contracts

    @api.multi
    def _compute_start_end_date(self):
        return
        # for agreement in self:
        #     active_contracts = agreement.get_active_contracts()
        #     sort_active_contracts = active_contracts.sorted(
        #         key=lambda l: (l.create_date, l.id))
        #     if sort_active_contracts:
        #         agreement.date_start = sort_active_contracts[-1].date_start
        #         agreement.date_end = sort_active_contracts[-1].date_end

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
            'context': {'active_test': False, },
            'domain': [('id', 'in', self.contract_ids.ids), ],
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
        ctx = dict(self._context or {})
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id),
             ], limit=1
        )
        today = fields.Date.context_today
        vals = ({
            'name': self.name,
            'contract_type': self.contract_type,
            'agreement_id': self.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
            'recurring_invoices': True,
            'recurring_interval': ctx.get('recurring_interval', 1),
            'recurring_rule_type': ctx.get('recurring_rule_type', 'monthly'),
            'date_start': ctx.get('date_start', today),
            'date_end': ctx.get('date_end', False),
            'recurring_next_date': ctx.get('date_start', today),
            'active': False,
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
    def create_new_contract(self):
        self.ensure_one()
        if self.is_contract_create:
            raise UserError(_('You created contract already.'))
        val = self.prepare_contract()
        contract = self.env['account.analytic.account'].create(val)
        vals = []
        for line in self.line_ids:
            new_line = self.prepare_contract_line(line)
            vals.append((0, 0, new_line))
        contract.write({'recurring_invoice_line_ids': vals})
        return contract
