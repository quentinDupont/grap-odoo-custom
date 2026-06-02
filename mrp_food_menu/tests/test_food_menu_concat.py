# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFoodMenuRecompute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Menu = cls.env["mrp.food.menu"]
        cls.MenuLine = cls.env["mrp.food.menu.line"]
        cls.Concat = cls.env["mrp.food.menu.concatenated.finished.boms"]
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]

        cls.product1 = cls.Product.create({"name": "Seitan"})
        cls.product2 = cls.Product.create({"name": "Houmous"})

        cls.bom1 = cls.Bom.create(
            {
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "type": "normal",
            }
        )

        cls.bom2 = cls.Bom.create(
            {
                "product_tmpl_id": cls.product2.product_tmpl_id.id,
                "type": "normal",
            }
        )

        cls.menu1 = cls.Menu.create({"name": "Menu 1"})

    def test_01_create_line_creates_concat(self):
        self.MenuLine.create(
            {
                "menu_id": self.menu1.id,
                "product_id": self.product1.id,
                "bom_id": self.bom1.id,
                "product_uom_qty": 5,
            }
        )

        concat = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product1.id),
                ("bom_id", "=", self.bom1.id),
            ]
        )

        self.assertEqual(len(concat), 1)
        self.assertEqual(concat.product_uom_qty, 5)

    def test_02_create_multiple_lines_sum(self):
        self.MenuLine.create(
            [
                {
                    "menu_id": self.menu1.id,
                    "product_id": self.product1.id,
                    "bom_id": self.bom1.id,
                    "product_uom_qty": 7,
                },
                {
                    "menu_id": self.menu1.id,
                    "product_id": self.product1.id,
                    "bom_id": self.bom1.id,
                    "product_uom_qty": 3,
                },
            ]
        )

        concat = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product1.id),
                ("bom_id", "=", self.bom1.id),
            ]
        )

        self.assertEqual(concat.product_uom_qty, 10)

    def test_03_write_qty_recompute(self):
        line = self.MenuLine.create(
            {
                "menu_id": self.menu1.id,
                "product_id": self.product1.id,
                "bom_id": self.bom1.id,
                "product_uom_qty": 4,
            }
        )

        line.write({"product_uom_qty": 10})

        concat = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product1.id),
                ("bom_id", "=", self.bom1.id),
            ]
        )

        self.assertEqual(concat.product_uom_qty, 10)

    def test_04_write_change_product_bom(self):
        line = self.MenuLine.create(
            {
                "menu_id": self.menu1.id,
                "product_id": self.product1.id,
                "bom_id": self.bom1.id,
                "product_uom_qty": 6,
            }
        )

        line.write(
            {
                "product_id": self.product2.id,
                "bom_id": self.bom2.id,
            }
        )

        concat_old = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product1.id),
            ]
        )
        concat_new = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product2.id),
            ]
        )

        self.assertFalse(concat_old)
        self.assertEqual(concat_new.product_uom_qty, 6)

    def test_05_unlink_recompute(self):
        line = self.MenuLine.create(
            {
                "menu_id": self.menu1.id,
                "product_id": self.product1.id,
                "bom_id": self.bom1.id,
                "product_uom_qty": 5,
            }
        )

        line.unlink()

        concat = self.Concat.search([("menu_id", "=", self.menu1.id)])
        self.assertFalse(concat)

    def test_06_write_multi_lines(self):
        lines = self.MenuLine.create(
            [
                {
                    "menu_id": self.menu1.id,
                    "product_id": self.product1.id,
                    "bom_id": self.bom1.id,
                    "product_uom_qty": 1,
                },
                {
                    "menu_id": self.menu1.id,
                    "product_id": self.product1.id,
                    "bom_id": self.bom1.id,
                    "product_uom_qty": 2,
                },
            ]
        )

        lines.write({"product_uom_qty": 5})

        concat = self.Concat.search(
            [
                ("menu_id", "=", self.menu1.id),
                ("product_id", "=", self.product1.id),
                ("bom_id", "=", self.bom1.id),
            ]
        )

        self.assertEqual(concat.product_uom_qty, 10)
