# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    p_width = fields.Float(
        string='Width',
    )
    p_length = fields.Float(
        string='Length',
    )
    p_area = fields.Float(
        string='Area',
    )
    working_hours = fields.Char()
    lease_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('compensation', 'Compensation'),
            ('deposit', 'Deposit'),
            ('transfer', 'Transfer'), ],
        string='Lease Type',
    )
    product_type = fields.Char()
    product_category = fields.Char()
