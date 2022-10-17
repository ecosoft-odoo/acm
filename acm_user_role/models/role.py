# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ResUsersRole(models.Model):
    _inherit = "res.users.role"

    is_readonly_user = fields.Boolean(
        string="Readonly User",
        default=False,
    )
    unrestrict_model_update = fields.Boolean(
        string="Unrestrict Model Update",
        default=False,
    )
    except_readonly_model_ids = fields.Many2many(
        comodel_name="ir.model",
        relation="res_users_role_ir_model_rel",
        column1="role_id",
        column2="model_id",
    )

    @api.multi
    def update_users(self):
        """Update readonly user"""
        res = super(ResUsersRole, self).update_users()
        users = self.sudo().mapped("user_ids")
        users.set_readonly_user_from_roles()
        return res

    @api.multi
    def unlink(self):
        users = self.sudo().mapped("user_ids")
        res = super(ResUsersRole, self).unlink()
        users.set_readonly_user_from_roles(force=True)
        return res


class ResUsersRoleLine(models.Model):
    _inherit = "res.users.role.line"

    @api.multi
    def unlink(self):
        users = self.mapped("user_id")
        res = super(ResUsersRoleLine, self).unlink()
        users.set_readonly_user_from_roles(force=True)
        return res
