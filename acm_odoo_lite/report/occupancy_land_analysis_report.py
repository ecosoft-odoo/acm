# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class OccupancyLandAnalysisReport(models.TransientModel):
    _name = 'occupancy.land.analysis.report'
    _description = 'Occupancy Land Analysis'

    product_id = fields.Many2one(
        comodel_name='product.template',
        index=True,
    )
    total_land_area_gla = fields.Float(
        string="Total Land Area (GLA)",
    )
    total_land_area_nla = fields.Float(
        string="Total Land Area (NLA)",
    )
    rented_land_area = fields.Float(
        string="Rented Land Area",
    )
    rented_land_percent = fields.Float(
        string="Rented Land (%)",
    )
    remaining_land_area = fields.Float(
        string="Remaining Land Area",
    )
    total_building_area = fields.Float(
        string="Total Building Area",
    )
    rented_building_area = fields.Float(
        string="Rented Building Area",
    )
    rented_building_percent = fields.Float(
        string="Rented Building (%)",
    )
    remaining_building_area = fields.Float(
        string="Remaining Building Area",
    )
    number_of_lessee  = fields.Integer(
        string="Number of Lessee",
    )
    number_of_agreement = fields.Integer(
        string="Number of Agreement",
    )
    lessor = fields.Char(
        string="Lessor",
    )
    wizard_id = fields.Many2one(
        comodel_name='occupancy.land.analysis.report.wizard',
        string='Wizard',
        index=True,
    )


class OccupancyLandAnalysisReportWizard(models.TransientModel):
    _name = 'occupancy.land.analysis.report.wizard'
    _description = 'Occupancy Land Analysis Report Wizard'

    at_date = fields.Date(
        string='At Date',
        required=True,
        default=fields.Date.context_today,
    ) 
    report_ids = fields.One2many(
        comodel_name='occupancy.land.analysis.report',
        inverse_name='wizard_id',
        string='Report',
    )

    @api.multi
    def _get_sql(self):
        self.ensure_one()
        sql = """
            select 
                pt.id as product_id, sub,lessor,
                (400 * pt.rai) + (100 * pt.ngan) + pt.square_wa as total_land_area_gla, 
                (400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2 as total_land_area_nla,
                sub.rented_land_area, sub.rented_land_area * 100 / coalesce(nullif(((400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2), 0), 1) as rented_land_percent,
                (((400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2) - sub.rented_land_area) as remaining_land_area,
                pt.square_meter2 as total_building_area, sub.rented_building_area, 
                ((sub.rented_building_area * 100) / coalesce(nullif(pt.square_meter2, 0), 1)) as rented_building_percent,
                (pt.square_meter2 - sub.rented_building_area) as remaining_building_area, sub.number_of_lessee, sub.number_of_agreement, {} as wizard_id
            from product_template pt
            left join product_product pp on pt.id = pp.product_tmpl_id
            left join (
                select pp.id, sum((400 * al.rai) + (100 * al.ngan) + al.square_wa) as rented_land_area,
                    sum(al.square_meter) as rented_building_area, count(distinct rp.id) as number_of_lessee,
                    count(distinct a.id) as number_of_agreement, string_agg(distinct ls.sequence_code, ',' order by ls.sequence_code) as lessor
                from agreement_line al
                left join agreement a on al.agreement_id = a.id
                left join res_partner rp on a.partner_id = rp.id
                left join res_partner ls on a.lessor_id = ls.id
                left join product_product pp on al.product_id = pp.id
                where a.is_template is False and (a.state = 'active' or (a.state = 'inactive' and a.inactive_reason <> 'cancel')) and 
                    '{}' >= a.start_date and '{}' <= (case when a.termination_date is not null then a.termination_date else a.end_date end)
                group by pp.id
            ) sub on pp.id = sub.id
            where pt.value_type = 'rent'
        """.format(self.id, self.at_date, self.at_date)
        return sql

    @api.multi
    def view_report(self):
        self.ensure_one()
        # Create Report
        self._cr.execute(self._get_sql())
        res = self._cr.dictfetchall()
        report = self.env['occupancy.land.analysis.report'].create(res)
        # View Report
        action = self.env.ref('acm_odoo_lite.occupancy_land_analysis_report_action')
        vals = action.read()[0]
        vals['domain'] = [('wizard_id', '=', self.id)]
        return vals
