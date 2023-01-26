# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Leased Land
    title_dead_no = fields.Char(
        string="Title Dead No."
    )
    parcel_no = fields.Char(
        string="Parcel No.",
    )
    vol = fields.Char(
        string="Volume",
    )
    page = fields.Char(
        string="Page",
    )
    sub_distinct_name = fields.Char(
        string="Sub-District Name",
    )
    distinct = fields.Char(
        string="Distinct",
    )
    province = fields.Char(
        string="Province",
    )
    # Leased Land Area
    rai = fields.Integer(
        string="Rai",
        default=0,
    )
    ngan = fields.Integer(
        string="Ngan",
        default=0,
    )
    square_wa = fields.Integer(
        string="Square Wa",
        default=0,
    )
