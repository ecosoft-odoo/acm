# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ZoneGroup(models.Model):
    """ Group of zones used to summarize the rental reports, e.g. the floor
    (Floor 1, Floor 2) or a group of zones (Zone A, Zone B). """
    _name = 'zone.group'
    _description = 'Zone Group'
    _order = 'sequence, name'

    name = fields.Char(
        required=True,
    )
    sequence = fields.Integer(
        default=10,
    )
    active = fields.Boolean(
        default=True,
    )
    zone_ids = fields.One2many(
        comodel_name='account.analytic.group',
        inverse_name='zone_group_id',
        string='Zones',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Zone Group must be unique!'),
    ]
