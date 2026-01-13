# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FoodMenu(models.Model):
    _name = "mrp.food.menu"
    _description = "Food menu"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        help="Menu name",
        required=True,
    )

    description = fields.Char(help="Field for external use, for example for PDF.")

    internal_notes = fields.Char(help="Field for internal use only.")

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda s: s._default_company_id(),
    )

    menu_line_ids = fields.One2many(
        comodel_name="mrp.food.menu.line",
        inverse_name="menu_id",
    )

    # Quick access to Products without any BoM
    product_wo_bom_ids = fields.One2many(
        comodel_name="product.product",
        compute="_compute_product_wo_bom_ids",
    )

    product_wo_bom_qty = fields.Integer(
        compute="_compute_product_wo_bom_qty",
    )

    # Concatenated BoM Lines
    concatenated_finished_bom_ids = fields.One2many(
        comodel_name="mrp.food.menu.concatenated.finished.boms",
        inverse_name="menu_id",
        compute="_compute_concatenated_finished_bom_ids",
        store=True,
    )

    # Methods for Products without any BoM
    @api.depends("menu_line_ids")
    def _compute_product_wo_bom_ids(self):
        for food_menu in self:
            food_menu.product_wo_bom_ids = food_menu.mapped(
                "menu_line_ids.product_id"
            ).filtered(lambda r: r.bom_count == 0)

    @api.depends("product_wo_bom_ids")
    def _compute_product_wo_bom_qty(self):
        for food_menu in self:
            food_menu.product_wo_bom_qty = len(food_menu.product_wo_bom_ids)

    # Methods for Concatenated BoM Lines
    # To be indempotent, we need to recomputer to sum well the same product qties
    def _recompute_concatenated_boms(self):
        Concat = self.env["mrp.food.menu.concatenated.finished.boms"]

        for menu in self:
            Concat.search([("menu_id", "=", menu.id)]).unlink()

            futur_concat = {}

            for line in menu.menu_line_ids.filtered(lambda x: not x.display_type):
                # Group by Product and BoM
                key = (line.product_id.id, line.bom_id.id)

                if key not in futur_concat:
                    futur_concat[key] = {
                        "menu_id": menu.id,
                        "date": line.date,
                        "product_id": line.product_id.id,
                        "bom_id": line.bom_id.id,
                        "product_uom_qty": 0.0,
                    }

                futur_concat[key]["product_uom_qty"] += line.product_uom_qty

            for vals in futur_concat.values():
                Concat.create(vals)

    # Default methods
    @api.model
    def _default_company_id(self):
        return self.env.company
