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
        states={'active': [('readonly', True)]},
        index=True,
        ondelete="restrict",
    )
    lessor_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor Contact",
        states={'active': [('readonly', True)]},
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
        states={'active': [('readonly', True)]},
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
        compute='_compute_is_contract_create',
    )
    is_payment_installment = fields.Boolean(
        string="Is Payment Installment",
        default=False,
    )
    payment_due_date = fields.Date(
        string="Payment Due Date",
    )
    payment_installment_ids = fields.One2many(
        comodel_name="agreement.payment.installment",
        inverse_name="agreement_id",
        string="Installment Line",
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
            "is_payment_installment": context.get("is_payment_installment") or self.is_payment_installment,
            "payment_due_date": context.get("payment_due_date") or self.payment_due_date,
        })
        payment_installment_ids = self.payment_installment_ids
        if context.get("payment_installment_ids"):
            payment_installment_ids = context["payment_installment_ids"]
        res["payment_installment_ids"] = [(0, 0, {"installment": i.installment, "payment_due_date": i.payment_due_date}) for i in payment_installment_ids]
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
                raise UserError(_('Please add Products/Services.'))
            # Agreement must have rental product
            if not rec.line_ids.filtered(lambda l: l.product_id.value_type == "rent"):
                raise UserError(_('Please add rental product.'))
        return True

    @api.model
    def _validate_rent_product_dates(self, product_lines):
        return True

    @api.constrains('line_ids')
    def _check_line_ids(self):
        return

    # Function used in appendix form
    def get_rental_product_area(self):
        self.ensure_one()
        products = self.line_ids.mapped("product_id")
        rental_products = products.filtered(lambda l: l.value_type == "rent")
        # Calculate area in square wa
        rai = sum(rental_products.mapped("rai"))
        ngan = sum(rental_products.mapped("ngan"))
        square_wa = sum(rental_products.mapped("square_wa"))
        area = (400 * rai) + (100 * ngan) + square_wa
        total_rai = int(area / 400)
        total_ngan = int((area - (400 * total_rai)) / 100)
        total_square_wa = area - (400 * total_rai) - (100 * total_ngan)
        return "{} ไร {} งาน {} ตารางวา".format(total_rai, total_ngan, total_square_wa)

    def get_rental_building_area(self):
        self.ensure_one()
        products = self.line_ids.mapped("product_id")
        building = products.filtered(
            lambda l: l.value_type == "rent" and l.has_building)
        square_meter = sum(building.mapped("square_meter"))
        return "{} ตารางเมตร".format(square_meter)


class AgreementPaymentInstallment(models.Model):
    _name = "agreement.payment.installment"
    _description = "Agreement Payment Installment"

    installment = fields.Integer(
        string="Installment",
        required=True,
        default=0,
    )
    payment_due_date = fields.Date(
        string="Payment Due Date",
        required=True,
    )
    agreement_id = fields.Many2one(
        comodel_name="agreement",
        index=True,
    )