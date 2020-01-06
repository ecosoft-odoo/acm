# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ContractCreateManualRentalInvoice(models.TransientModel):
    _name = 'contract.create.manual.rental.invoice'
    _inherit = 'contract.create.manual.invoice'
    _description = 'Create Manual Rental Invoice From Contract'

    @api.model
    def _get_product_ids(self):
        active_ids = self._context.get('active_ids', [])
        Contract = self.env['account.analytic.account']
        contracts = Contract.browse(active_ids)
        product_ids = contracts and \
            set(contracts.mapped('recurring_invoice_line_ids').
                filtered(lambda l: l.manual and
                         l.product_id.value_type == 'rent').
                mapped('product_id').ids) or set()
        return list(product_ids)

    @api.model
    def default_get(self, fields):
        res = super(ContractCreateManualRentalInvoice, self).default_get(
            fields)
        res['product_ids'] = self._get_product_ids()
        return res

    @api.model
    def _get_product_domain(self):
        if self._context.get('active_model') != 'account.analytic.account':
            return []
        return [('id', 'in', self._get_product_ids())]

    @api.multi
    def _check_create_manual_invoice(self, contract, date_invoice, products):
        super(ContractCreateManualRentalInvoice, self). \
            _check_create_manual_invoice(contract, date_invoice, products)
        lines = contract.recurring_invoice_line_ids.filtered(
            lambda l: l.manual and l.product_id.value_type == 'rent')
        if not lines:
            raise ValidationError(
                _("This contract '%s' doesn't have rental product." % (
                    contract.name, )))
