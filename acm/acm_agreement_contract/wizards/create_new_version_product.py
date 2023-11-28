# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class CreateNewVersionProduct(models.TransientModel):
    _name = 'create.new.version.product'
    _description = 'Create New Version Product'

    @api.model
    def default_get(self, field_list):
        active_ids = self._context.get('active_ids', [])
        products = self.env['product.template'].browse(active_ids)
        value_type_list = list(set(products.mapped('value_type')))
        year_list = list(set(products.mapped('year')))
        version_list = list(set(products.mapped('version')))
        is_lastest_version_list = list(set(products.mapped('is_lastest_version')))
        # This action for rent product only
        if value_type_list != ['rent']:
            raise UserError(_(
                'There are some selected product not rent product, '
                'this action required for rent product only.'
            ))
        # Year and version are required
        if False in year_list or False in version_list:
            raise UserError(_('Year and version are required for rent product.'))
        # Create new product version from lastest version only
        if is_lastest_version_list != [True]:
            raise UserError(_('Create new product version from lastest version only.'))
        return super(CreateNewVersionProduct, self).default_get(field_list)

    @api.multi
    def action_create_new_version(self):
        active_ids = self._context.get('active_ids', [])
        products = self.env['product.template'].browse(active_ids)
        new_products = self.env['product.template']
        for product in products:
            # Update lastest version from True to False
            product.write({'is_lastest_version': False})
            if self._context.get('next_year'):
                year = self._context['next_year']
                version = '0001'
            else:
                # New Version = Lastest Version + 1
                year = product.year
                version = str(int(product.version) + 1).zfill(4)
                # No allowed create a new version
                agreements = self.env['agreement'].search([
                    ('active_date', '!=', False),
                    ('rent_product_id', 'in', product.product_variant_ids.ids),
                ])
                termination_date_list = [a.termination_date if a.termination_date else a.end_date for a in agreements]
                today = fields.Date.context_today(self)
                if termination_date_list and today <= max(termination_date_list):
                    raise UserError(_('No allowed create a new version for product has agreement ({})').format(product.name))
                if str(today.year) != year:
                    raise UserError(_('No allowed create a new version on different year.'))
                if not (product.date_start and not product.date_end):
                    raise UserError(_('The product must have product start date and not product end date.'))
            new_product = product.copy(
                default={
                    'year': year,
                    'version': version,
                    'is_lastest_version': True,
                    'origin_product_template_id': product.id,
                }
            )
            new_product._onchange_year_version_group_subzone_lock_number()
            if product.year == new_product.year:
                new_product_date = (new_product.create_date + relativedelta(hours=7)).date()
                product.date_end = new_product_date - relativedelta(days=1)
                new_product.date_start = new_product_date
            # Create Pricelist
            pricelist = self.env['acm.product.pricelist'].create({
                'product_template_id': new_product.id,
            })
            pricelist._onchange_product_template_id()
            new_products |= new_product
        # Redirect to product view
        action = self.env.ref('product.product_template_action').read()[0]
        action.update({
            'domain': [('id', 'in', new_products.ids)],
        })
        if len(new_products) == 1:
            action.update({
                'views': [(self.env.ref('product.product_template_only_form_view').id, 'form')],
                'res_id': new_products.id
            })
        return action
