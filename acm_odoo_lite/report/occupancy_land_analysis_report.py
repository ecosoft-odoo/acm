# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class OccupancyLandAnalysisReport(models.TransientModel):
    _name = "occupancy.land.analysis.report"
    _description = "Occupancy Land Analysis"

    product_name = fields.Char(
        string="Product",
    )
    title_deed_no = fields.Char(
        string="Title Deed No.",
    )
    parcel_no = fields.Char(
        string="Parcel No.",
    )
    vol = fields.Char(
        string="Volume",
    )
    page = fields.Char(
        string="Page",
    )
    sub_district = fields.Char(
        string="Sub-District",
    )
    district = fields.Char(
        string="District",
    )
    province = fields.Char(
        string="Province",
    )
    rai = fields.Integer(
        string="Rai",
    )
    ngan = fields.Integer(
        string="Ngan",
    )
    square_wa = fields.Float(
        string="Square Wa",
        digits=(16, 2),
    )
    rai2 = fields.Integer(
        string="Rai2",
    )
    ngan2 = fields.Integer(
        string="Ngan2",
    )
    square_wa2 = fields.Float(
        string="Square Wa2",
        digits=(16, 2),
    )
    lessor = fields.Char(
        string="Lessor",
    )
    total_land_area_gla = fields.Float(
        string="Total Land Area (GLA) (SQW)",
        digits=(16, 2),
    )
    total_land_area_nla = fields.Float(
        string="Total Land Area (NLA) (SQW)",
        digits=(16, 2),
    )
    rented_land_area = fields.Float(
        string="Rented Land Area (SQW)",
        digits=(16, 2),
    )
    rented_land_percent = fields.Float(
        string="Rented Land (%)",
        digits=(16, 2),
    )
    remaining_land_area = fields.Float(
        string="Remaining Land Area (SQW)",
        digits=(16, 2),
    )
    total_building_area = fields.Float(
        string="Total Building Area (SQM)",
        digits=(16, 2),
    )
    rented_building_area = fields.Float(
        string="Rented Building Area (SQM)",
        digits=(16, 2),
    )
    rented_building_percent = fields.Float(
        string="Rented Building (%)",
        digits=(16, 2),
    )
    remaining_building_area = fields.Float(
        string="Remaining Building Area (SQM)",
        digits=(16, 2),
    )
    number_of_lessee = fields.Integer(
        string="Number of Lessee",
    )
    number_of_agreement = fields.Integer(
        string="Number of Agreement",
    )
    partner_list = fields.Char(
        string="Partner List",
    )
    agreement_list = fields.Char(
        string="Agreement List",
    )
    wizard_id = fields.Many2one(
        comodel_name="occupancy.land.analysis.report.wizard",
        string="Wizard",
        index=True,
    )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(OccupancyLandAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if "__domain" in line:
                # Rented Land (%)
                line["rented_land_percent"] = line["rented_land_area"] * 100 / (line["total_land_area_nla"] or 1)
                # Rented Building (%)
                line["rented_building_percent"] = line["rented_building_area"] * 100 / (line["total_building_area"] or 1)
                # Number of Lessee, Number of Agreement
                report = self.search(line["__domain"])
                partner_list = []
                agreement_list = []
                for r in report:
                    if r.partner_list:
                        partner_list += eval(r.partner_list)
                    if r.agreement_list:
                        agreement_list += eval(r.agreement_list)
                line["number_of_lessee"] = len(list(set(partner_list)))
                line["number_of_agreement"] = len(list(set(agreement_list)))
        return res


class OccupancyLandAnalysisReportWizard(models.TransientModel):
    _name = "occupancy.land.analysis.report.wizard"
    _description = "Occupancy Land Analysis Report Wizard"

    at_date = fields.Date(
        string="At Date",
        required=True,
        default=fields.Date.context_today,
    )
    report_ids = fields.One2many(
        comodel_name="occupancy.land.analysis.report",
        inverse_name="wizard_id",
        string="Report",
    )

    @api.multi
    def _get_sql(self):
        self.ensure_one()
        sql = """
            select
                pt.name as product_name, pt.title_deed_no, pt.parcel_no, pt.vol, pt.page, pt.sub_district,
                pt.district, pt.province, pt.rai, pt.ngan, pt.square_wa, pt.rai2, pt.ngan2, pt.square_wa2, sub,lessor,
                (400 * pt.rai) + (100 * pt.ngan) + pt.square_wa as total_land_area_gla,
                (400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2 as total_land_area_nla,
                sub.rented_land_area, sub.rented_land_area * 100 / coalesce(nullif(((400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2), 0), 1) as rented_land_percent,
                (((400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2) - sub.rented_land_area) as remaining_land_area,
                pt.square_meter2 as total_building_area, sub.rented_building_area,
                ((sub.rented_building_area * 100) / coalesce(nullif(pt.square_meter2, 0), 1)) as rented_building_percent,
                (pt.square_meter2 - sub.rented_building_area) as remaining_building_area, sub.number_of_lessee, sub.number_of_agreement, sub.partner_list,
                sub.agreement_list, {} as wizard_id
            from product_template pt
            left join product_product pp on pt.id = pp.product_tmpl_id
            left join (
                select pp.id, sum((400 * al.rai) + (100 * al.ngan) + al.square_wa) as rented_land_area,
                    sum(al.square_meter) as rented_building_area, count(distinct rp.id) as number_of_lessee,
                    count(distinct a.id) as number_of_agreement, string_agg(distinct ls.sequence_code, ',' order by ls.sequence_code) as lessor,
                    '[' || string_agg(distinct rp.id::char, ',' order by rp.id::char) || ']' as partner_list,
                    '[' || string_agg(distinct a.id::char, ',' order by a.id::char) || ']' as agreement_list
                from agreement_line al
                left join agreement a on al.agreement_id = a.id
                left join res_partner rp on a.partner_id = rp.id
                left join res_partner ls on a.lessor_id = ls.id
                left join product_product pp on al.product_id = pp.id
                where a.is_template = False and (a.state = 'active' or (a.state = 'inactive' and a.inactive_reason <> 'cancel')) and
                    '{}' >= a.start_date and '{}' <= (case when a.termination_date is not null then a.termination_date else a.end_date end)
                group by pp.id
            ) sub on pp.id = sub.id
            where pt.value_type = 'rent' and pt.active = True
        """.format(self.id, self.at_date, self.at_date)
        return sql

    @api.multi
    def view_report(self):
        self.ensure_one()
        # Create Report
        self._cr.execute(self._get_sql())
        res = self._cr.dictfetchall()
        self.env["occupancy.land.analysis.report"].create(res)
        # View Report
        action = self.env.ref("acm_odoo_lite.occupancy_land_analysis_report_action")
        vals = action.read()[0]
        vals["domain"] = [("wizard_id", "=", self.id)]
        return vals
