/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.changes.nombre_facturacion_fel = this.props.partner.nombre_facturacion_fel || false;
    },
    async saveChanges() {
        const vat = this.changes.vat;
        if (vat) {
            var datos_facturacion_fel = await this.orm.silent.call("res.partner", "obtener_partner_name_con_datos_sat", [this.props.partner, this.pos.company.id, this.changes.vat]);
            console.log(datos_facturacion_fel)
            if(!datos_facturacion_fel.nombre || datos_facturacion_fel.mensaje){
                return this.popup.add(ErrorPopup, {
                    title: _t("Datos no encontrados: %s", datos_facturacion_fel.mensaje),
                });
            }else{
                await this.popup.add(ConfirmPopup, {
                    title: _t("Datos de facturación:"),
                    body: _t("NIT/CUI: %s   NOMBRE: %s", datos_facturacion_fel.nit, datos_facturacion_fel.nombre),
                });
                if (!this.props.partner.parent_name){
                    this.changes.name = datos_facturacion_fel.nombre
                }
                this.changes.nombre_facturacion_fel = datos_facturacion_fel.nombre
            }
        }
        return super.saveChanges(...arguments);
    }
});