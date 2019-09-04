# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer'),
            ('purchase', 'Supplier'),
        ],
        default="sale",
    )
    contract_count = fields.Integer(
        string="Contract_count",
        compute="_compute_contract_count",
    )

    @api.multi
    def _compute_contract_count(self):
        for contract in self:
            search_contract = contract.env['account.analytic.account'].\
                search([('agreement_id', '=', self.id)])
            if search_contract:
                contract.contract_count = len(search_contract)

    @api.multi
    def action_view_contract(self):
        contract = self.env['account.analytic.account']
        search_contract = contract.search([('agreement_id', '=', self.id)])
        if not search_contract:
            raise UserError(
                _('Please create contract.'))
        if self.contract_type == 'sale':
            action = self.env.ref(
                'contract.action_account_analytic_sale_overdue_all').read()[0]
            action['views'] = [(self.env.ref(
                'contract.account_analytic_account_sale_form').id, 'form')]
        else:
            action = self.env.ref(
                'contract.action_account_analytic_purchase_overdue_all').\
                read()[0]
            action['views'] = [(self.env.ref(
                'contract.account_analytic_account_purchase_form').id, 'form')]
        action['res_id'] = search_contract.id
        return action

    @api.multi
    def create_new_contract(self, journal=None):
        self.ensure_one()
        if self.contract_count != 0:
            raise UserError(
                _('You created contract already.'))
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id),
             ], limit=1
        )
        # Prepare contract
        vals = self.env['account.analytic.account'].create({
            'name': self.name,
            'contract_type': self.contract_type,
            'agreement_id': self.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'recurring_invoices': True,
        })
        vals._onchange_date_start()
        # Prepare contract's product lines
        for line in self.line_ids:
            line = self.env['account.analytic.invoice.line'].create({
                'analytic_account_id': vals.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.qty,
                'uom_id': line.uom_id.id,
                'price_unit': line.product_id.lst_price,
            })
        # Action view
        if self.contract_type == 'sale':
            view_id = self.env.ref(
                'contract.account_analytic_account_sale_form').id
        else:
            view_id = self.env.ref(
                'contract.account_analytic_account_purchase_form').id
        view_contract = {
            'res_id': vals.id,
            'view_id': view_id,
            'res_model': 'account.analytic.account',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
        }
        return view_contract
