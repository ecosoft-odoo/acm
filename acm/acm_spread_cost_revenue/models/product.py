# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    spread_template_id = fields.Many2one(
        comodel_name='account.spread.template',
        string='Spread Cost/Revenue Template',
    )
    use_invoice_line_account = fields.Boolean(
        string='Use Invoice Line Account',
        related='spread_template_id.use_invoice_line_account',
    )
    spread_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Spread B/L Account',
        related='spread_template_id.spread_account_id',
    )
    exp_rev_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Expense/Revenue Account',
        related='spread_template_id.exp_rev_account_id',
    )
    spread_over = fields.Selection(
        [("contract", "Contract's Start Date -> End Date"),
         ("template", "Template's Number of Repetitions")],
        string="Spread Over",
        default="contract",
        required=True,
    )
