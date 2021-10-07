odoo.define('fenix_mass_invoicing_billing.mass_account_move', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var FormController = require('web.FormController');
var FormRenderer = require('web.FormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var _t = core._t;
var QWeb = core.qweb;

var MassAccountFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        button_process_clicked: '_onClick_button_process',
    }),

    MAX_PROCESS_TIMEOUT: 500,

    _buttonProcess: function(ev, kw={ prefetch: true, }) {
        var record = this.model.get(ev.data.record.id);
        return this._rpc({
            model: this.modelName,
            method: 'button_process_json',
            args: [record.res_id],
            kwargs: kw,
        }, {
            shadow: true,
        });
    },

    _onClick_button_process: function(ev) {
        ev.stopPropagation();
        var self = this;

        $.blockUI({ message: QWeb.render('MassInvoice.Process.Loader'), });

        const processPromise = this._buttonProcess(ev);
        processPromise.then(res => {
            const _queueProcess = r => {
                if ((_.has(r, 'orders_count') && r.orders_count > 0) && r.partner) {
                    self._buttonProcessTimeout = setTimeout(() => {
                        $('.massinvoice_blockui_message').html(QWeb.render('MassInvoice.Process.Loader.Message', r || {}));
                        return self._buttonProcess(ev, r)
                            .then(_queueProcess)
                            .guardedCatch(_queueProcess);
                    }, self.MAX_PROCESS_TIMEOUT);
                } else {
                    $.unblockUI();
                    return self.update({mode: self.mode || 'readonly'}, {reload: true});
                };
            };
            return _queueProcess(res);
        }).guardedCatch(() => { $.unblockUI(); });
    },
});

var MassAccountFormRenderer = FormRenderer.extend({
    _addOnClickAction: function ($el, node) {
        var self = this;
        if (_.has(node.attrs, 'id') && node.attrs.id === "queue_process") {
            $el.on("click", function () {
                self.trigger_up('button_process_clicked', {
                    attrs: node.attrs,
                    record: self.state,
                });
            });
            return true;
        };
        this._super.apply(this, arguments);
    },
});

var MassAccountMoveFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: MassAccountFormController,
        Renderer: MassAccountFormRenderer,
    }),
});

viewRegistry.add('js_mass_account_move', MassAccountMoveFormView);

});
