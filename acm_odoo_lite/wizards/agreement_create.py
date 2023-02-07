# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _inherit = "agreement.create"

    income_type_id = fields.Many2one(
        required=False,
    )
    partner_id = fields.Many2one(
        string="Lessee",
    )
    partner_contact_id = fields.Many2one(
        string="Lessee Contact",
    )
    lessor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor",
        required=True,
    )
    lessor_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor Contact",
    )
    post_name = fields.Char(
        required=False,
    )
    recurring_interval = fields.Integer(
        required=False,
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'),
        ],
        required=False,
    )
    payment_type = fields.Selection(
        selection=[
            ("full_paid", "Full Paid"),
            ("installment", "Installment"),
        ],
        string="Payment Type",
        required=True,
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
    def action_create_agreement(self):
        """ Create Agreement """
        self.ensure_one()
        self = self.with_context({
            "lessor_id": self.lessor_id.id,
            "lessor_contact_id": self.lessor_contact_id.id,
            "payment_type": self.payment_type,
            "payment_date": self.payment_date,
            "installment_number": self.installment_number,
            "payment_every_days": self.payment_every_days,
            "payment_every_months": self.payment_every_months,
        })
        res = super(AgreementCreate, self).action_create_agreement()
        return res

    @api.onchange("payment_type")
    def _onchange_payment_type(self):
        self.update({
            "payment_date": False,
            "installment_number": 1,
            "payment_every_days": False,
            "payment_every_months": False,
            "recurring_rule_type": False,
        })
