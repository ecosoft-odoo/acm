# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ContractCreateInvoice(models.TransientModel):
    _name = 'contract.create.invoice'
    _description = 'Create Invoice From Contract'

    multi = fields.Boolean(
        default=lambda self: len(self._context.get('active_ids', [])) > 1,
    )
    num_inv_advance = fields.Integer(
        string='Create invoices in advance',
        default=1,
    )
    next_date_ids = fields.One2many(
        comodel_name='contract.create.invoice.date',
        inverse_name='wizard_id',
        string='Next invoice dates'
    )

    @api.onchange('num_inv_advance')
    def _onchange_num_inv_advance(self):
        self.next_date_ids = False
        active_ids = self._context.get('active_ids', [])
        Contract = self.env['account.analytic.account']
        contracts = Contract.browse(active_ids)
        dates = contracts.mapped('recurring_next_date')
        dates = [fields.Date.to_string(x) for x in list(set(dates))]
        if self.num_inv_advance > 1:
            contracts.ensure_one()
            contract = contracts[0]
            ref_date = contract.recurring_next_date or fields.Date.today()
            for i in range(self.num_inv_advance-1):
                old_date = fields.Date.from_string(ref_date)
                ref_date = old_date + Contract.get_relative_delta(
                    contract.recurring_rule_type, contract.recurring_interval)
                dates.append(fields.Date.to_string(ref_date))
        dates.sort()
        dates = [(0, 0, {'date': x}) for x in dates]
        self.next_date_ids = dates

    @api.multi
    def action_create_invoices(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        # Do not allow to create invoice in advance, when working with multi
        if self.multi and len(self.next_date_ids) > 1:
            raise UserError(
                _('Multiple next dates not allowed when working in batch'))
        contracts = self.env['account.analytic.account'].browse(active_ids)
        invoices = self.env['account.invoice']
        for i in range(self.num_inv_advance):
            invoices |= contracts.recurring_create_invoice()
        return self.view_invoices(contracts, invoices)

    @api.multi
    def view_invoices(self, contracts, invoices):
        self.ensure_one()
        if len(list(set(contracts.mapped('contract_type')))) > 1:
            return True
        action = self.env.ref(
            'contract.act_purchase_recurring_invoices')
        if contracts[0].contract_type == 'sale':
            action = self.env.ref(
                'contract.act_recurring_invoices')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % (invoices.ids)
        return result


class ContractCreateInvoiceDate(models.TransientModel):
    _name = 'contract.create.invoice.date'
    _description = 'Invoice Dates'

    wizard_id = fields.Many2one(
        comodel_name='contract.create.invoice',
    )
    date = fields.Date(
        string='Next Invoice Date',
    )
