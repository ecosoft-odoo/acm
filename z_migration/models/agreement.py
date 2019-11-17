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

    @api.multi
    def mock_unlink_recital_structure(self):
        self.mapped('recital_ids').unlink()
        return True

    @api.multi
    def mock_unlink_section_structure(self):
        self.mapped('sections_ids').unlink()
        return True

    @api.multi
    def mock_unlink_clause_structure(self):
        self.mapped('clauses_ids').unlink()
        return True

    @api.multi
    def mock_unlink_appendix_structure(self):
        self.mapped('appendix_ids').unlink()
        return True

    @api.multi
    def mock_copy_recital_structure(self):
        self.ensure_one()
        for rec in self.template_id.recital_ids:
            recital = rec.copy()
            recital.agreement_id = self.id
        return True

    @api.multi
    def mock_copy_section_structure(self):
        self.ensure_one()
        for rec in self.template_id.sections_ids:
            section = rec.copy()
            section.agreement_id = self.id
            section.mapped('clauses_ids').write({
                'agreement_id': self.id,
            })
        return True

    @api.multi
    def mock_copy_appendix_structure(self):
        self.ensure_one()
        for rec in self.template_id.appendix_ids:
            appendix = rec.copy()
            appendix.agreement_id = self.id
        return True
