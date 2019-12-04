# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ACMWorkingHours(models.Model):
    _name = 'acm.working.hours'
    _description = 'ACM Working Hours'

    name = fields.Char(
        required=True,
    )
    working_hours = fields.Char(
        required=True,
    )
    type = fields.Selection(
        selection=[
            ('in_time', 'In Time'),
            ('out_time', 'Out Time'),
        ],
    )
