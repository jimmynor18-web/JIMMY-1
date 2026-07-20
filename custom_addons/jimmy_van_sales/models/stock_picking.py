# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            if picking.picking_type_code not in ("outgoing", "internal"):
                continue
            necesidades = {}
            for move in picking.move_ids:
                if move.state in ("done", "cancel"):
                    continue
                producto = move.product_id
                almacenable = getattr(
                    producto, "is_storable",
                    getattr(producto, "type", "") == "product",
                )
                if not almacenable:
                    continue
                cantidad = move.product_uom._compute_quantity(
                    move.product_uom_qty, producto.uom_id
                )
                necesidades[producto] = necesidades.get(producto, 0.0) + cantidad

            faltantes = []
            for producto, requerido in necesidades.items():
                disponible = producto.with_context(
                    location=picking.location_id.id
                ).qty_available
                if float_compare(
                    disponible, requerido,
                    precision_rounding=producto.uom_id.rounding,
                ) < 0:
                    faltantes.append(
                        "  • %s: se necesitan %s y hay %s"
                        % (producto.display_name, requerido, disponible)
                    )
            if faltantes:
                raise UserError(_(
                    "No hay existencias suficientes en la ubicación %s "
                    "para validar esta operación:\n\n%s\n\n"
                    "Revise el inventario (Inventario → Informes → Existencias), "
                    "registre la compra, producción o traslado que falta, "
                    "o ajuste las cantidades del documento."
                ) % (picking.location_id.display_name, "\n".join(faltantes)))
        return super().button_validate()
