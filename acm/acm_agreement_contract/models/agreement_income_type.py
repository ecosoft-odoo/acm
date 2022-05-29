# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AgreementIncomeType(models.Model):
    _name = 'agreement.income.type'

    name = fields.Char(
        string='Name',
        required=True,
    )
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('lump_sum_rent', 'Lump Sum Rent'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'),
        ],
        string='Value Type',
        required=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        required=True,
        index=True,
    )
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='income_type_tax',
        column1='type_id',
        column2='tax_id',
        string='Taxes',
    )
