# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float()
    length = fields.Float()
    area = fields.Float()
    working_hours = fields.Char()
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('tea_money', 'Tea Money'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'), ],
        string='Value Type',
    )
    product_type = fields.Char(
        string='Product Types',
    )
    product_category = fields.Char(
        string='Product Categories',
    )
