# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    type2 = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('utility', 'Utility'),
            ('toilet', 'Toilet'),
            ('others', 'Others'),
        ],
        string='Invoice Type',
    )
    rent_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        string='Product',
        store=True,
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='rent_product_id.group_id',
        string='Zone',
        store=True,
    )

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_product_id(self):
        for rec in self:
            rent_products = rec.invoice_line_ids.filtered(
                lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            if rent_products:
                rec.rent_product_id = rent_products[0]
