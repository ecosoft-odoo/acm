# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api
from lxml import etree


class Agreement(models.Model):
    _inherit = 'agreement'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(Agreement, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        root = etree.fromstring(res['arch'])
        root.set('create', 'true')
        root.set('edit', 'true')
        root.set('duplicate', 'true')
        root.set('delete', 'true')
        res['arch'] = etree.tostring(root)
        return res
