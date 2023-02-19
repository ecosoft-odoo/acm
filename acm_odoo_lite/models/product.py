# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Title Deed Information
    title_deed_no = fields.Char(
        string="Title Deed No."
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
    sub_district = fields.Char(
        string="Sub-District",
    )
    district = fields.Char(
        string="District",
    )
    province = fields.Char(
        string="Province",
    )
    map = fields.Binary(
        string='Map',
    )
    # Title Deed Area (GLA)
    rai = fields.Integer(
        string="Rai",
        default=0,
    )
    ngan = fields.Integer(
        string="Ngan",
        default=0,
    )
    square_wa = fields.Float(
        string="Square Wa",
        default=0,
        digits=(16, 2),
    )
    square_meter = fields.Float(
        string="Square Meter",
        default=0,
        digits=(16, 2),
    )
    # Title Deed Area (NLA)
    rai2 = fields.Integer(
        string="Rai",
        default=0,
    )
    ngan2 = fields.Integer(
        string="Ngan",
        default=0,
    )
    square_wa2 = fields.Float(
        string="Square Wa",
        default=0,
        digits=(16, 2),
    )
    square_meter2 = fields.Float(
        string="Square Meter",
        default=0,
        digits=(16, 2),
    )
    remaining_land = fields.Char(
        compute="_compute_remaining_area",
        string="Remaining Land For Rent",
    )
    remaining_building = fields.Char(
        compute="_compute_remaining_area",
        string="Remaining Building For Rent",
    )

    @api.constrains("rai", "ngan", "square_wa", "square_meter", "rai2", "ngan2", "square_wa2", "square_meter2")
    def _check_area(self):
        for rec in self:
            nla_area = (400 * rec.rai2) + (100 * rec.ngan2) + rec.square_wa2
            gla_area = (400 * rec.rai) + (100 * rec.ngan) + rec.square_wa
            if nla_area > gla_area or rec.square_meter2 > rec.square_meter:
                raise UserError(_("Title deed area (nla) must less than or equal to title deed area (gla)."))

    @api.multi
    def _get_remaining_area(self):
        self.ensure_one()
        remaining_area = 0
        remaining_building_area = 0
        if self.value_type == "rent":
            products = self.env["product.product"].search([("product_tmpl_id", "=", self.id)])
            agreement_lines = self.env["agreement.line"].search([
                ("agreement_id.state", "in", ["draft", "active"]), ("product_id", "in", products.ids)])
            rent_rai_area = sum(agreement_lines.mapped("rai"))
            rent_ngan_area = sum(agreement_lines.mapped("ngan"))
            rent_square_wa_area = sum(agreement_lines.mapped("square_wa"))
            rent_area = (400 * rent_rai_area) + (100 * rent_ngan_area) + rent_square_wa_area
            total_area = (400 * self.rai2) + (100 * self.ngan2) + self.square_wa2
            remaining_area = total_area - rent_area
            rent_building_area = sum(agreement_lines.mapped("square_meter"))
            total_building_area = self.square_meter2
            remaining_building_area = total_building_area - rent_building_area
        return (remaining_area, remaining_building_area)

    @api.multi
    def _compute_remaining_area(self):
        for rec in self:
            if rec.value_type == "rent":
                # Compute remaining land
                remaining_area = rec._get_remaining_area()
                remaining_land_rai = int(remaining_area[0] / 400)
                remaining_land_ngan = int((remaining_area[0] - (400 * remaining_land_rai)) / 100)
                remaining_land_square_wa = remaining_area[0] - (400 * remaining_land_rai) - (100 * remaining_land_ngan)
                if remaining_land_square_wa == int(remaining_land_square_wa):
                    str_remaining_land_square_wa = str(int(remaining_land_square_wa))
                else:
                    str_remaining_land_square_wa = "{0:,.2f}".format(remaining_land_square_wa)
                rec.remaining_land = "{} rai {} ngan {} square wa".format(remaining_land_rai, remaining_land_ngan, str_remaining_land_square_wa)
                # Compute remaining building
                remaining_building_square_meter = remaining_area[1]
                if remaining_building_square_meter == int(remaining_building_square_meter):
                    str_remaining_building_square_meter = str(int(remaining_building_square_meter))
                else:
                    str_remaining_building_square_meter = "{0:,.2f}".format(remaining_building_square_meter)
                rec.remaining_building = "{} square meter".format(str_remaining_building_square_meter)
            else:
                rec.remaining_land = ""
                rec.remaining_building = ""
