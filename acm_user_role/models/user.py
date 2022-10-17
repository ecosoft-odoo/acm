# Copyright 2022 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        res.set_readonly_user_from_roles()
        return res

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.set_readonly_user_from_roles()
        return res
        
    @api.multi
    def set_readonly_user_from_roles(self, force=False):
        for user in self:
            if not user.role_line_ids and not force:
                continue
            update_val = {
                "is_readonly_user": False,
                "unrestrict_model_update": False,
                "except_readonly_model_ids": [(6, 0, [])],
            }
            except_readonly_model_ids = self.env["ir.model"]
            for role_line in user._get_applicable_roles():
                role = role_line.role_id
                if not role:
                    continue
                # Update fields
                if role.is_readonly_user:
                    update_val["is_readonly_user"] = role.is_readonly_user
                    except_readonly_model_ids |= role.except_readonly_model_ids
                if role.unrestrict_model_update:
                    update_val["unrestrict_model_update"] = role.unrestrict_model_update
            if except_readonly_model_ids:
                update_val["except_readonly_model_ids"] = [(6, 0, except_readonly_model_ids.ids)]
            # If field updated, write field into the user
            if not (update_val["is_readonly_user"] == user["is_readonly_user"] and \
                update_val["unrestrict_model_update"] == user["unrestrict_model_update"] and \
                except_readonly_model_ids == user["except_readonly_model_ids"]):
                    super(ResUsers, user).write(update_val)             
        return True
