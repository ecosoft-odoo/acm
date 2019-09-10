# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AgreementGenre(models.Model):
    _name = "agreement.genre"
    _description = "Agreement Genres"

    name = fields.Char(
        string="Title",
        required=True,
    )
