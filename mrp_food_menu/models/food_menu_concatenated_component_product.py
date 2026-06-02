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
    _order = "product_category_name, product_name"

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

    menu_state = fields.Selection(
        related="menu_id.state",
    )

    company_id = fields.Many2one(
        related="menu_id.company_id",
    )

    date = fields.Date()

    bom_ids = fields.Many2many(
        string="Used in BoMs",
        comodel_name="mrp.bom",
    )

    concatenated_details = fields.One2many(
        comodel_name="mrp.food.menu.concatenated.component.product.detail",
        inverse_name="concat_component_product",
        string="Detail per BoMs",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
    )

    product_name = fields.Char(
        related="product_id.display_name",
        string="Product Name",
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
        string="Quantity with Purchase UoM",
        compute="_compute_product_po_uom_qty",
        digits="Product Quantity",
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
        string="Product Category Name",
        store=True,
    )

    product_tag_ids = fields.Many2many(
        comodel_name="product.tag",
        related="product_id.product_tag_ids",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="product_id.currency_id",
    )

    standard_price = fields.Float(
        string="Unit Standard Price",
        related="product_id.standard_price",
        digits="Product Unit of Measure",
    )

    subtotal_standard_price = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal_standard_price",
        digits="Product Unit of Measure",
    )

    received = fields.Boolean()

    @api.depends("product_id", "product_uom_qty", "product_uom_id", "product_uom_po_id")
    def _compute_product_po_uom_qty(self):
        for concat_product in self:
            factor = (
                concat_product.product_uom_po_id.factor
                / concat_product.product_uom_id.factor
                if concat_product.product_uom_id.factor != 0
                else 1
            )
            concat_product.product_uom_po_qty = concat_product.product_uom_qty * factor

    @api.depends("product_id", "product_uom_qty", "standard_price")
    def _compute_subtotal_standard_price(self):
        for concat_product in self:
            concat_product.subtotal_standard_price = (
                concat_product.product_uom_qty * concat_product.standard_price
            )

    def print_pdf_report(self):
        self.ensure_one()
        return self.env.ref(
            "mrp_food_menu.food_menu_concatenated_component_report"
        ).report_action(self)
