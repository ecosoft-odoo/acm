# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import tools
from odoo import models, fields, api


class RentalCollectReport(models.Model):
    _name = 'rental.collect.report'
    _description = 'Rental Collect Report'
    _auto = False
    _order = 'product_name'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
    )
    product_name = fields.Char()
    partner_id = fields.Many2one(
        comodel_name='res.partner',
    )
    goods_type = fields.Char()
    lst_price = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection(
        selection=[
            ('drafe', 'Draft'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW rental_collect_report as (
                select
                    pt.id,
                    pt.group_id,
                    pt.name as product_name,
                    ag.partner_id,
                    pt.goods_type,
                    agl.lst_price,
                    agl.date_start,
                    agl.date_end,
                    ag.state
                from
                    product_template pt
                    left join product_product pp on pt.id = pp.product_tmpl_id
                    left join agreement_line agl on pp.id = agl.product_id
                    and agl.id = (select max(id) from agreement_line agl2
                    where agl2.agreement_id = agl.agreement_id)
                    left join agreement ag on agl.agreement_id = ag.id
                    where pt.value_type = 'rent'
                    order by pt.lock_number, pt.group_id
            )
        """)

    @api.model
    def trans_months(self, month):
        months = {
            '01': 'มกราคม',
            '02': 'กุมภาพันธ์',
            '03': 'มีนาคม',
            '04': 'เมษายน',
            '05': 'พฤษภาคม',
            '06': 'มิถุนายน',
            '07': 'กรกฎาคม',
            '08': 'สิงหาคม',
            '09': 'กันยายน',
            '10': 'ตุลาคม',
            '11': 'พฤศจิกายน',
            '12': 'ธันวาคม',
        }
        return months[month]
