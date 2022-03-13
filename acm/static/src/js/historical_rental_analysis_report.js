odoo.define("acm_reports.historical_rental_analysis_report", function (require) {
    "use strict";

    var ListController = require("web.ListController");

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if ((this.modelName === "historical.occupancy.analysis.report" || this.modelName === "historical.rental.rate.analysis.report") && this.$buttons) {
                var self = this;
                var data = this.model.get(this.handle);
                // Hide create and import button
                this.$buttons.find(".o_list_button_add").hide();
                this.$buttons.find(".o_button_import").hide()
                // Show lessee info
                this.$buttons
                    .find(".lessee_info")
                    .on("click", function () {
                        self.do_action(
                            "acm.lessee_info_wizard_action",
                            {
                                additional_context: data.context,
                            }
                        );
                    });
            }
        },
    };

    ListController.include(includeDict);
});
