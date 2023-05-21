# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
from datetime import date
from odoo.addons import decimal_precision as dp


class HistoricalRentalAnalysisReport(models.AbstractModel):
    _name = 'historical.rental.analysis.report'
    _description = 'Historical Rental Analysis Report'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        index=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        index=True,
    )
    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        string='Attribute Values',
        related='product_id.attribute_value_ids',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Lessee',
        index=True,
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
        index=True,
    )
    goods_category_id = fields.Many2one(
        comodel_name='goods.category',
        string='Goods Category',
        index=True,
    )
    start_date = fields.Date(
        string='Start Date',
        index=True,
    )
    end_date = fields.Date(
        string='End Date',
        index=True,
    )
    area = fields.Float(
        string='Area For Lease',
        digits=dp.get_precision('Area'),
    )
    occupied_area = fields.Float(
        string='Area Occupied',
        digits=dp.get_precision('Area'),
    )
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('lump_sum_rent', 'Lump Sum Rent'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'), ],
        string='Value Type',
        index=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        index=True,
    )

    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None,
    #                orderby=False, lazy=True):
    #     res = super(HistoricalRentalAnalysisReport, self).read_group(
    #         domain, fields, groupby, offset=offset, limit=limit,
    #         orderby=orderby, lazy=lazy)
    #     for line in res:
    #         if '__domain' in line:
    #             report = self.search(line['__domain'])
    #             # Area For Lease
    #             self._cr.execute("""
    #                 SELECT product_tmpl_id, area
    #                 FROM "{}"
    #                 WHERE id IN %s
    #                 GROUP BY product_tmpl_id, area""".format(self._table), (
    #                     tuple(report.ids), ))
    #             line['area'] = sum(map(
    #                 lambda l: l['area'], self._cr.dictfetchall()))
    #             # Area Occupied
    #             self._cr.execute("""
    #                 SELECT product_tmpl_id, area
    #                 FROM "{}"
    #                 WHERE id IN %s AND agreement_id IS NOT NULL
    #                 GROUP BY product_tmpl_id, area""".format(self._table), (
    #                     tuple(report.ids), ))
    #             line['occupied_area'] = sum(map(
    #                 lambda l: l['area'], self._cr.dictfetchall()))
    #     return res

    @api.model
    def _get_sql_area_select(self, else_value=0):
        select = """
            CASE WHEN pt.area IS NOT NULL AND pt.area <> 0
            THEN pt.area ELSE %s END
        """ % (else_value, )
        return select

    @api.model
    def _get_sql_area_occupied_select(self, else_value=0):
        select = """
            CASE WHEN a.id IS NOT NULL AND pt.area IS NOT NULL AND pt.area <> 0
            THEN pt.area ELSE %s END
        """ % (else_value, )
        return select

    @api.model
    def _get_sql(self):
        at_date = self._context.get("at_date").strftime("%Y-%m-%d")
        at_date = "DATE('{}')".format(at_date)
        sql = """
            SELECT ROW_NUMBER() OVER(ORDER BY pp.id, a.id) AS id,
                   pt.group_id, pp.id AS product_id, a.partner_id,
                   a.id AS agreement_id, a.goods_category_id, a.start_date,
                   a.end_date, %(area_select)s AS area, %(area_occupied_select)s AS occupied_area, pt.value_type,
                   pp.product_tmpl_id
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN agreement a ON pp.id = a.rent_product_id AND
            a.state != 'draft' AND a.active_date IS NOT NULL AND %(at_date)s BETWEEN a.start_date AND
            (CASE
                WHEN a.termination_date IS NOT NULL THEN a.termination_date
                WHEN a.inactive_date IS NULL THEN a.end_date
                WHEN a.inactive_date IS NOT NULL AND a.inactive_date > a.end_date THEN a.end_date
                ELSE a.inactive_date
            END)
            WHERE pt.value_type = 'rent' AND pp.active IS TRUE
        """
        sql = sql % {
            'area_select': self._get_sql_area_select(),
            'area_occupied_select': self._get_sql_area_occupied_select(),
            'at_date': at_date,
        }
        return sql
