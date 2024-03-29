# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    active = fields.Boolean(
        string='Active',
        default=True,
    )
