# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ACMBreachType(models.Model):
    _name = 'acm.breach.type'
    _description = 'ACM Breach Type'

    name = fields.Char()
