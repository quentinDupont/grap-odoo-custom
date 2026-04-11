# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


# The aim is to sum the quantities of each Finished Products of the Menu
# So there is just one line per Products / BoM per Food Menu
class FoodMenuMrpConcatenatedFinishedBoms(models.Model):
    _name = "mrp.food.menu.concatenated.finished.boms"
    _description = "Food Menu all Concatenated Finished BoMs"

    _sql_constraints = [
        (
            "uniq_menu_concat_finish_product_bom",
            "unique(menu_id, product_id, bom_id)",
            "Duplicate concatenated Finished BoM line",
        ),
    ]

    menu_id = fields.Many2one(
        comodel_name="mrp.food.menu",
        required=True,
    )

    company_id = fields.Many2one(
        related="menu_id.company_id",
    )

    date = fields.Datetime()

    product_id = fields.Many2one(
        comodel_name="product.product",
    )

    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        required=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
    )

    product_category_id = fields.Many2one(
        comodel_name="product.category",
        related="product_id.categ_id",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="product_id.currency_id",
    )

    lst_price = fields.Float(
        related="product_id.lst_price",
    )

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
    )

    subtotal = fields.Float(
        compute="_compute_subtotal",
    )

    @api.depends("product_uom_qty", "lst_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_uom_qty * line.lst_price
