# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree


class Agreement(models.Model):
    _inherit = "agreement"

    income_type_id = fields.Many2one(
        required=False,
    )
    lessor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor",
        states={"active": [("readonly", True)]},
        index=True,
        ondelete="restrict",
    )
    lessor_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor Contact",
        states={"active": [("readonly", True)]},
        index=True,
        ondelete="restrict",
    )
    lessor_contact_phone = fields.Char(
        related="lessor_contact_id.phone",
        string="Lessor Phone",
    )
    lessor_contact_email = fields.Char(
        related="lessor_contact_id.email",
        string="Lessor Email",
    )
    lessor_witness = fields.Char(
        string="Lessor Witness",
        states={"active": [("readonly", True)]},
    )
    company_id = fields.Many2one(
        string="Company",
    )
    company_contact_id = fields.Many2one(
        string="Company Contact",
    )
    company_contact_phone = fields.Char(
        string="Phone",
    )
    company_contact_email = fields.Char(
        string="Email",
    )
    all_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_all_product_ids",
        string="Products",
    )
    special_terms = fields.Text(
        states={"active": [("readonly", False)]},
    )
    is_contract_create = fields.Boolean(
        compute="_compute_is_contract_create",
    )
    recurring_interval = fields.Integer(
        required=False,
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ("monthly", "Month(s)"),
            ("yearly", "Year(s)"),
        ],
        required=False,
        states={"active": [("readonly", False)]},
    )
    payment_type = fields.Selection(
        selection=[
            ("full_paid", "Full Paid"),
            ("installment", "Installment"),
        ],
        string="Payment Type",
    )
    payment_date = fields.Date(
        string="Payment Date",
    )
    installment_number = fields.Integer(
        string="Installment Number",
        default=1,
    )
    payment_every_days = fields.Integer(
        string="Payment Every (Days)",
    )
    payment_every_months = fields.Selection(
        selection=[
            ("01", "มกราคม"),
            ("02", "กุมภาพันธ์"),
            ("03", "มีนาคม"),
            ("04", "เมษายน"),
            ("05", "พฤษภาคม"),
            ("06", "มิถุนายน"),
            ("07", "กฤกฎาคม"),
            ("08", "สิงหาคม"),
            ("09", "กันยายน"),
            ("10", "ตุลาคม"),
            ("11", "พฤศจิกายน"),
            ("12", "ธันวาคม"),
        ],
        string="Payment Every (Months)",
    )

    @api.multi
    def _compute_is_contract_create(self):
        """ Bypass check is contract create """
        for rec in self:
            rec.is_contract_create = True

    @api.multi
    def _compute_all_product_ids(self):
        """ Get all products """
        for rec in self:
            rec.all_product_ids = rec.line_ids.mapped("product_id")

    @api.onchange("payment_type")
    def _onchange_payment_type(self):
        self.update({
            "payment_date": False,
            "installment_number": 1,
            "payment_every_days": False,
            "payment_every_months": False,
            "recurring_rule_type": False,
        })

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Change width of column products on the tree view """
        res = super(Agreement, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == "tree":
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//field[@name='all_product_ids']"):
                node.set("style", "width: min-content")
            res["arch"] = etree.tostring(doc)
        return res

    @api.multi
    def get_agreement_vals(self):
        res = super(Agreement, self).get_agreement_vals()
        context = self._context.copy()
        res.update({
            "lessor_id": context.get("lessor_id") or self.lessor_id.id,
            "lessor_contact_id": context.get("lessor_contact_id") or self.lessor_contact_id.id,
            "payment_type": context.get("payment_type") or self.payment_type,
            "payment_date": context.get("payment_date") or self.payment_date,
            "installment_number": context.get("installment_number") or self.installment_number,
            "payment_every_days": context.get("payment_every_days") or self.payment_every_days,
            "payment_every_months": context.get("payment_every_months") or self.payment_every_months,
        })
        return res

    @api.model
    def create(self, vals):
        code = vals.get("code")
        lessor_id = vals.get("lessor_id")
        if vals.get("code", _("New")) and lessor_id:
            partner = self.env["res.partner"].browse(lessor_id)
            sequence = False
            if partner.lessor and partner.sequence_id:
                sequence = partner.sequence_id.next_by_id()
                vals.update({
                    "code": sequence,
                    "name": sequence,
                    "description": sequence,
                })
            if not sequence:
                raise UserError(_("Sequence code is not defined in lessor."))
        agreement = super(Agreement, self).create(vals)
        return agreement

    @api.onchange("lessor_id")
    def _onchange_lessor_id(self):
        if not self.is_template and self.lessor_id and self.code != "New":
            raise UserError(_("Lessor is not allowed to change on the agreement"))

    @api.multi
    def _validate_active_agreement(self):
        """ Validate agreement before active """
        for rec in self:
            # Agreement must be state to draft
            if rec.state != 'draft':
                raise UserError(_("Agreement's state must be draft."))
            # Agreement must have products/services
            if not rec.line_ids:
                raise UserError(_("Please add Products/Services."))
            # Agreement must have rental product
            if not rec.line_ids.filtered(lambda l: l.product_id.value_type == "rent"):
                raise UserError(_("Please add rental product."))
        return True

    @api.model
    def _validate_rent_product_dates(self, product_lines):
        return True

    @api.constrains("line_ids")
    def _check_line_ids(self):
        return

    # Function used in appendix form
    def get_rental_area(self):
        self.ensure_one()
        agreement_lines = self.line_ids.filtered(lambda l: l.product_id.value_type == "rent")
        # Calculate area in square wa
        rai = sum(agreement_lines.mapped("rai"))
        ngan = sum(agreement_lines.mapped("ngan"))
        square_wa = sum(agreement_lines.mapped("square_wa"))
        area = (400 * rai) + (100 * ngan) + square_wa
        total_rai = int(area / 400)
        total_ngan = int((area - (400 * total_rai)) / 100)
        total_square_wa = area - (400 * total_rai) - (100 * total_ngan)
        if total_square_wa == int(total_square_wa):
            str_total_square_wa = str(int(total_square_wa))
        else:
            str_total_square_wa = "{0:,.2f}".format(total_square_wa)
        return "{} ไร {} งาน {} ตารางวา".format(total_rai, total_ngan, str_total_square_wa)

    def get_rental_building_area(self):
        self.ensure_one()
        agreement_lines = self.line_ids.filtered(lambda l: l.product_id.value_type == "rent")
        square_meter = sum(agreement_lines.mapped("square_meter"))
        if square_meter == int(square_meter):
            str_square_meter = str(int(square_meter))
        else:
            str_square_meter = "{0:,.2f}".format(square_meter)
        return "{} ตารางเมตร".format(str_square_meter)


class AgreementLine(models.Model):
    _inherit = "agreement.line"

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
        string="Square Meter For Building",
        default=0,
        digits=(16, 2),
    )
    value_type = fields.Selection(
        related="product_id.value_type",
    )
    remaining_land = fields.Char(
        related="product_id.product_tmpl_id.remaining_land",
    )
    remaining_building = fields.Char(
        related="product_id.product_tmpl_id.remaining_building",
    )
    product_id = fields.Many2one(
        required=True,
    )
    lst_price = fields.Float(
        required=True,
    )

    @api.multi
    def _validate_product(self):
        self.ensure_one()
        # Check product do not duplicate
        agreement_lines = self.env["agreement.line"].search([
            ("agreement_id", "=", self.agreement_id.id),
            ("product_id", "=", self.product_id.id),
            ("agreement_id.state", "not in", ["active"]), # State active will not check product
        ])
        if len(agreement_lines) > 1:
            raise UserError(_("Product do not duplicate on the agreement lines."))
        # Check rental area
        remaining_area = self.product_id.product_tmpl_id._get_remaining_area()
        if remaining_area[0] < 0:
            area = remaining_area[0] + (400 * self.rai) + (100 * self.ngan) + self.square_wa
            rai = int(area / 400)
            ngan = int((area - (400 * rai)) / 100)
            square_wa = area - (400 * rai) - (100 * ngan)
            if square_wa == int(square_wa):
                str_square_wa = str(int(square_wa))
            else:
                str_square_wa = "{0:,.2f}".format(square_wa)
            raise UserError(_("{} not enough area to rent (Remaining area: {} rai {} ngan {} square wa).").format(self.name, rai, ngan, str_square_wa))
        if remaining_area[1] < 0:
            square_meter = remaining_area[1] + self.square_meter
            if square_meter == int(square_meter):
                str_square_meter = str(int(square_meter))
            else:
                str_square_meter = "{0:,.2f}".format(square_meter)
            raise UserError(_("{} not enough building area to rent (Remaining area: {} square meter).").format(self.name, str_square_meter))
        return True

    @api.model
    def create(self, vals):
        agreement_line = super(AgreementLine, self).create(vals)
        # Validate Product
        agreement_line._validate_product()
        return agreement_line

    @api.multi
    def write(self, vals):
        res = super(AgreementLine, self).write(vals)
        for line in self:
            # Validate Product
            line._validate_product()
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        """ Reset area and price """
        self.update({
            "rai": 0,
            "ngan": 0,
            "square_wa": 0,
            "square_meter": 0,
            "lst_price": 0,
        })
