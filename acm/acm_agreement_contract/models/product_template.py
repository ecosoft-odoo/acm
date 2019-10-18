# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float()
    length = fields.Float()
    area = fields.Float()
    working_hours = fields.Char()
    lease_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('compensation', 'Compensation'),
            ('deposit', 'Deposit'),
            ('transfer', 'Transfer'), ],
        string='Lease Type',
    )
