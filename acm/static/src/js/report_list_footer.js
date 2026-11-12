odoo.define("acm_reports.report_list_footer", function (require) {
    "use strict";

    /**
     * List view whose footer totals are computed by the server.
     *
     * The standard list footer sums the values loaded in the browser: only the
     * records of the current page, and a plain sum of the group values (wrong
     * for an average like the Average Rental Rate). Here the footer of each
     * column with a ``sum`` attribute shows the value of ``read_group`` without
     * groupby, i.e. computed by the report on all records of the search (or on
     * the selected records).
     *
     * Usage: <tree js_class="report_server_total_list"> + sum="Total" on fields
     */
    var core = require("web.core");
    var ListRenderer = require("web.ListRenderer");
    var ListView = require("web.ListView");
    var utils = require("web.utils");
    var viewRegistry = require("web.view_registry");

    var _t = core._t;

    var ReportListRenderer = ListRenderer.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.serverTotals = null;
            this.serverTotalsKey = null;
        },

        //----------------------------------------------------------------------
        // Private
        //----------------------------------------------------------------------

        /**
         * @private
         * @returns {string[]} names of the numeric columns having a sum attribute
         */
        _getTotalFields: function () {
            var self = this;
            return _.chain(this.columns)
                .filter(function (column) {
                    var field = self.state.fields[column.attrs.name];
                    return column.attrs.sum && field &&
                        _.contains(["integer", "float", "monetary"], field.type);
                })
                .map(function (column) { return column.attrs.name; })
                .value();
        },
        /**
         * Fetch the totals from the server (cached for a same search/selection)
         *
         * @private
         * @returns {Deferred}
         */
        _fetchTotals: function () {
            var self = this;
            var fields = this._getTotalFields();
            if (!fields.length) {
                this.serverTotals = null;
                return $.when();
            }
            var domain = this.state.domain || [];
            if (this.selection.length) {
                var resIds = [];
                utils.traverse_records(this.state, function (record) {
                    if (_.contains(self.selection, record.id)) {
                        resIds.push(record.res_id);
                    }
                });
                domain = [["id", "in", resIds]];
            }
            var context = this.state.getContext ? this.state.getContext() : {};
            var key = JSON.stringify([this.state.model, domain, fields, context]);
            if (key === this.serverTotalsKey) {
                return $.when();
            }
            // Only the last request may update the totals (the selection can
            // change again before the previous totals are received)
            var requestId = this.totalsRequestId = (this.totalsRequestId || 0) + 1;
            return this._rpc({
                model: this.state.model,
                method: "read_group",
                kwargs: {
                    domain: domain,
                    fields: fields,
                    groupby: [],
                    lazy: false,
                },
                context: context,
            }).then(function (result) {
                if (requestId !== self.totalsRequestId) {
                    return $.Deferred().reject();
                }
                self.serverTotals = (result && result[0]) || {};
                self.serverTotalsKey = key;
            });
        },
        /**
         * @override
         */
        _computeColumnAggregates: function (data, column) {
            if (this.serverTotals && column.attrs.sum &&
                    _.contains(this._getTotalFields(), column.attrs.name)) {
                column.aggregate = {
                    help: column.attrs.sum,
                    value: this.serverTotals[column.attrs.name] || 0,
                };
                return;
            }
            this._super.apply(this, arguments);
        },
        /**
         * Add a "Total" label in the first footer cell without value
         *
         * @override
         */
        _renderFooter: function () {
            var $footer = this._super.apply(this, arguments);
            if (this.serverTotals) {
                var $cells = $footer.find("td");
                // skip the record selector cell
                var $cell = $cells.filter(function () {
                    return !$(this).text().trim();
                }).eq(this.hasSelectors ? 1 : 0);
                $cell.text(_t("Total")).css("font-weight", "bold");
            }
            return $footer;
        },
        /**
         * @override
         */
        _renderView: function () {
            var _super = this._super.bind(this);
            return this._fetchTotals().then(function () {
                return _super();
            }, function () {
                // Totals failed or outdated by a newer request: render anyway,
                // the newer request updates the footer when received
                return _super();
            });
        },
        /**
         * @override
         */
        _updateFooter: function () {
            var self = this;
            var _super = this._super.bind(this);
            return this._fetchTotals().then(function () {
                _super();
            });
        },
    });

    var ReportListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: ReportListRenderer,
        }),
    });

    viewRegistry.add("report_server_total_list", ReportListView);

    return {
        ReportListRenderer: ReportListRenderer,
        ReportListView: ReportListView,
    };
});
