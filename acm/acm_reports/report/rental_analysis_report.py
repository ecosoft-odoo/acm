# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, tools


class RentalAnalysisReport(models.Model):
    _name = 'rental.analysis.report'
    _description = 'Rental Analysis Report'
    _auto = False

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
    )
    subzone = fields.Char(
        string='Subzone',
    )
    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        string='Attribute Values',
        related='product_id.attribute_value_ids',
    )
    start_date = fields.Date(
        string='Agreement Start Date',
    )
    end_date = fields.Date(
        string='Agreement End Date',
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
    )
    area = fields.Float(
        string='Area For Lease',
    )
    occupied_area = fields.Float(
        string='Area Occupied',
    )
    occupancy = fields.Float(
        string='Occupancy',
    )

    @api.model
    def _get_sql(self):
        sql = """
            SELECT ROW_NUMBER() OVER(ORDER BY pp.id, a.id) AS id,
                   pp.id AS product_id, pt.group_id, pt.subzone,
                   a.start_date, a.end_date, a.id AS agreement_id,
                   -- Area For Lease
                   CASE WHEN pt.area IS NOT NULL THEN pt.area
                   ELSE 0 END AS area,
                   -- Area Occupied
                   CASE WHEN a.id IS NOT NULL AND NOW() >= a.start_date AND
                   NOW() <= a.end_date AND pt.area IS NOT NULL THEN pt.area
                   ELSE 0 END AS occupied_area,
                   -- Occupancy
                   (CASE WHEN a.id IS NOT NULL AND NOW() >= a.start_date AND
                   NOW() <= a.end_date AND pt.area IS NOT NULL THEN pt.area
                   ELSE 0 END) / (CASE WHEN pt.area IS NOT NULL AND
                   pt.area <> 0 THEN pt.area ELSE 1 END) AS occupancy
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN agreement a ON pp.id = a.rent_product_id AND
            a.state = 'active'
            WHERE pt.value_type = 'rent' AND pp.active IS TRUE
        """
        return sql

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)""" % (
            self._table, self._get_sql()))
