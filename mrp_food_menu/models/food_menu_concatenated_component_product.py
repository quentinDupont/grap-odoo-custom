# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


# The aim is to sum the quantities of each Component Products of the Menu
# So there is just one line per Products per Food Menu
class FoodMenuMrpConcatenatedComponentProduct(models.Model):
    _name = "mrp.food.menu.concatenated.component.product"
    _description = "Food Menu all Concatenated Component Products"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date, product_category_id, product_name"

    _sql_constraints = [
        (
            "uniq_menu_concat_component_product",
            "unique(menu_id, product_id, date)",
            "Duplicate concatenated Component Menu-Product-Date",
        ),
    ]

    menu_id = fields.Many2one(
        comodel_name="mrp.food.menu",
        required=True,
    )

    company_id = fields.Many2one(
        related="menu_id.company_id",
    )

    date = fields.Date()

    bom_ids = fields.Many2many(
        string="Used in BoMs",
        comodel_name="mrp.bom",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
    )

    product_name = fields.Char(
        related="product_id.display_name",
        string="Product",
        store=True,
    )

    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Quantity",
        required=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
    )

    product_uom_po_qty = fields.Float(
        string="Quantity",
        digits="Product Quantity with Purchase Unit of Measure",
        compute="_compute_product_po_uom_qty",
    )

    product_uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase Unit of Measure",
        related="product_id.uom_po_id",
    )

    product_category_id = fields.Many2one(
        comodel_name="product.category",
        related="product_id.categ_id",
        store=True,
    )

    product_category_name = fields.Char(
        related="product_category_id.complete_name",
        string="Product Category",
        store=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="product_id.currency_id",
    )

    standard_price = fields.Float(
        related="product_id.standard_price",
    )

    @api.depends("product_id", "product_uom_qty", "product_uom_id", "product_uom_po_id")
    def _compute_product_po_uom_qty(self):
        for concat_product in self:
            factor = (
                concat_product.product_uom_po_id.factor / concat_product.product_uom_id.factor
                if concat_product.product_uom_id.factor != 0
                else 1
            )
            concat_product.product_uom_po_qty = (
                concat_product.product_uom_qty * factor
            )
