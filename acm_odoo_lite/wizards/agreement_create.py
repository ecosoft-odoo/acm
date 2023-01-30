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
    is_payment_installment = fields.Boolean(
        string="Is Payment Installment",
        default=False,
    )
    payment_due_date = fields.Date(
        string="Payment Due Date",
    )
    payment_installment_ids = fields.One2many(
        comodel_name="agreement.create.payment.installment",
        inverse_name="wizard_id",
        string="Installment Line",
    )

    @api.multi
    def action_create_agreement(self):
        """ Create Agreement """
        self.ensure_one()
        self = self.with_context({
            "lessor_id": self.lessor_id.id,
            "lessor_contact_id": self.lessor_contact_id.id,
            "is_payment_installment": self.is_payment_installment,
            "payment_due_date": self.payment_due_date,
            "payment_installment_ids": self.payment_installment_ids,
        })
        res = super(AgreementCreate, self).action_create_agreement()
        return res


class AgreementCreatePaymentInstallment(models.TransientModel):
    _name = "agreement.create.payment.installment"
    _description = "Agreement Create Payment Installment"

    installment = fields.Integer(
        string="Installment",
        required=True,
        default=0,
    )
    payment_due_date = fields.Date(
        string="Payment Due Date",
        required=True,
    )
    wizard_id = fields.Many2one(
        comodel_name="agreement.create",
        index=True,
    )
