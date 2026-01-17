# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


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

    # Concatenated Products and BoMs
    concatenated_component_products_ids = fields.One2many(
        comodel_name="mrp.food.menu.concatenated.component.product",
        inverse_name="menu_id",
    )

    concatenated_intermediate_bom_ids = fields.One2many(
        comodel_name="mrp.food.menu.concatenated.intermediate.boms",
        inverse_name="menu_id",
    )

    concatenated_finished_bom_ids = fields.One2many(
        comodel_name="mrp.food.menu.concatenated.finished.boms",
        inverse_name="menu_id",
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

    ### Methods for Concatenated BoM Lines

    # Lire les lignes :
    # 1) du Menu qui ont pas de BoM → genre du pain à acheter
    # 2) des Finished BoMs, en filtrant les lignes qui seront dans Intermediate
    # 3) des Intermediate BoMs
    # Créer les lignes de produits à acheter
    # On regroupe pas par Produit car on veut aussi l'info de la date où le produit est nécessaire
    def _compute_concatenated_component_products(self):
        Concat_component_prod = self.env["mrp.food.menu.concatenated.component.product"]
        Concat_inter_bom = self.env["mrp.food.menu.concatenated.intermediate.boms"]
        Concat_finished_bom = self.env["mrp.food.menu.concatenated.finished.boms"]

        for menu in self:
            # Delete all lines to recompute them
            print("============ 1) Direct les MP du Menu genre le pain")
            Concat_component_prod.search([("menu_id", "=", menu.id)]).unlink()
            futur_concat_component = {}

            # 1) Line without BoM → directly component (e.g bread)
            for line in menu.menu_line_ids.filtered(lambda x: not x.bom_id):
                # Group by Product
                key = (line.product_id.id, line.date.date() if line.date else False)

                if key not in futur_concat_component:
                    futur_concat_component[key] = {
                        "menu_id": menu.id,
                        "date": line.date.date() if line.date else False,
                        "product_id": line.product_id.id,
                        "product_uom_qty": 0.0,
                    }

                # import pdb; pdb.set_trace()
                futur_concat_component[key]["product_uom_qty"] += line.product_uom_qty

            # 2) Product lines of finished BoMs without lines of intermediate product
            concat_finished_boms = Concat_finished_bom.search(
                [
                    ("menu_id", "=", menu.id),
                ]
            )
            print("============ 2) Produits des FT finis")
            for concat_finished_bom in concat_finished_boms:
                for bom_line in concat_finished_bom.mapped(
                    "bom_id.bom_line_ids"
                ).filtered(lambda x: x.product_id.bom_count == 0):
                    # Group by Product
                    key = (
                        bom_line.product_id.id,
                        concat_finished_bom.date.date()
                        if concat_finished_bom.date
                        else False,
                    )

                    if key not in futur_concat_component:
                        futur_concat_component[key] = {
                            "menu_id": menu.id,
                            "date": concat_finished_bom.date.date()
                            if concat_finished_bom.date
                            else False,
                            "product_id": bom_line.product_id.id,
                            "product_uom_qty": 0.0,
                            "bom_ids": [Command.link(bom_line.bom_id.id)],
                        }

                    # import pdb; pdb.set_trace()
                    # Quantité de recette de lignes concaténées * la quantité du produit dans la recette (divisée par les unités de la recette)
                    futur_concat_component[key]["product_uom_qty"] += (
                        concat_finished_bom.product_uom_qty
                        * bom_line.product_qty
                        / bom_line.bom_id.product_qty
                        * bom_line.bom_id.product_uom_id.factor
                    )

            # 3) Product lines of intermediate BoMs
            concat_inter_boms = Concat_inter_bom.search(
                [
                    ("menu_id", "=", menu.id),
                ]
            )
            print("============ 3) Produits des FT intermediate")
            for concat_inter_bom in concat_inter_boms:
                for bom_line in concat_inter_bom.mapped("bom_id.bom_line_ids"):
                    # Group by Product
                    key = (
                        bom_line.product_id.id,
                        concat_inter_bom.date.date()
                        if concat_inter_bom.date
                        else False,
                    )

                    if key not in futur_concat_component:
                        futur_concat_component[key] = {
                            "menu_id": menu.id,
                            "date": concat_inter_bom.date.date()
                            if concat_inter_bom.date
                            else False,
                            "product_id": bom_line.product_id.id,
                            "product_uom_qty": 0.0,
                            "bom_ids": [Command.link(bom_line.bom_id.id)],
                        }

                    # import pdb; pdb.set_trace()
                    # Quantité de recette de lignes concaténées * la quantité du produit dans la recette (divisée par les unités de la recette)
                    futur_concat_component[key]["product_uom_qty"] += (
                        concat_inter_bom.product_uom_qty
                        * bom_line.product_qty
                        / bom_line.bom_id.product_qty
                        * bom_line.bom_id.product_uom_id.factor
                    )

        for vals in futur_concat_component.values():
            Concat_component_prod.create(vals)

    # En entrée : les lignes déjà concaténées finies pour avoir les bonnes qtés
    # Puis diguer dedans pour voir les BoM contenant des lignes avec des produits qui ont un BoM
    # Intermediate BoMs
    def _compute_concatenated_inter_boms(self):
        Concat_finished_bom = self.env["mrp.food.menu.concatenated.finished.boms"]
        Concat_inter_bom = self.env["mrp.food.menu.concatenated.intermediate.boms"]

        for menu in self:
            # chercher les lignes concaténés, ligne contenant un BoM
            concat_finished_boms = Concat_finished_bom.search(
                [
                    ("menu_id", "=", menu.id),
                    ("bom_id", "!=", False),
                ]
            )

            # Delete all lines to recompute them
            Concat_inter_bom.search([("menu_id", "=", menu.id)]).unlink()
            futur_concat_inter = {}

            for concat_finished_bom in concat_finished_boms:
                # parcourir les lignes de recette voir lequels sont intermédiaires
                for bom_line in concat_finished_bom.bom_id.bom_line_ids.filtered(
                    lambda x: x.product_id.bom_count > 0
                ):
                    # Group by BoM
                    key = bom_line.bom_id.id

                    if key not in futur_concat_inter:
                        futur_concat_inter[key] = {
                            "menu_id": menu.id,
                            "date": concat_finished_bom.date,
                            "product_id": bom_line.product_id.id,
                            "bom_id": bom_line.product_id.bom_ids[
                                0
                            ].id,  # Limitation : arbitraly we choose 1st BoM
                            "product_uom_qty": 0.0,
                        }

                    futur_concat_inter[key]["product_uom_qty"] += (
                        bom_line.product_qty * concat_finished_bom.product_uom_qty
                    )

            for vals in futur_concat_inter.values():
                Concat_inter_bom.create(vals)

    # Finished BoMs
    def _compute_concatenated_finished_boms(self):
        Concat_finished_bom = self.env["mrp.food.menu.concatenated.finished.boms"]

        for menu in self:
            # Delete all lines to recompute them
            Concat_finished_bom.search([("menu_id", "=", menu.id)]).unlink()

            futur_concat_finished = {}

            for line in menu.menu_line_ids.filtered(
                lambda x: not x.display_type and x.bom_id
            ):
                # Group by Product and BoM
                key = (line.product_id.id, line.bom_id.id)

                if key not in futur_concat_finished:
                    futur_concat_finished[key] = {
                        "menu_id": menu.id,
                        "date": line.date,
                        "product_id": line.product_id.id,
                        "bom_id": line.bom_id.id,
                        "product_uom_qty": 0.0,
                    }

                futur_concat_finished[key]["product_uom_qty"] += line.product_uom_qty

            for vals in futur_concat_finished.values():
                Concat_finished_bom.create(vals)

    # To be indempotent, we need to recomputer to sum well the same product qties
    def compute_concatenated_boms_products(self):
        for menu in self:
            # Launch finished boms computation
            menu._compute_concatenated_finished_boms()

            # Launch intermediate boms computation
            menu._compute_concatenated_inter_boms()

            # Launch component products computation
            menu._compute_concatenated_component_products()

    # Default methods
    @api.model
    def _default_company_id(self):
        return self.env.company
