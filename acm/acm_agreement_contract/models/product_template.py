# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float(
        default=0,
    )
    length = fields.Float(
        default=0,
    )
    area = fields.Float(
        default=0,
    )
    time_start = fields.Float(
        default=0,
    )
    time_end = fields.Float(
        default=0,
    )
