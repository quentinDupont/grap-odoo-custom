# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FoodMenuMrpConcatenatedComponentProductDetail(models.Model):
    _name = "mrp.food.menu.concatenated.component.product.detail"
    _description = "Food Menu all Concatenated Component Products Detail"

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
    )

    quantity = fields.Float()

    product_uom_po_id = fields.Many2one(
        related="concat_component_product.product_uom_po_id"
    )

    concat_component_product = fields.Many2one(
        comodel_name="mrp.food.menu.concatenated.component.product",
    )
