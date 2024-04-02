# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMrpFoodBom(TransactionCase):
    def setUp(self):
        super(TestMrpFoodBom, self).setUp()
        self.bom_tomato_tart = self.env.ref("mrp_food.demo_bom_tomato_tart")
        self.bom_tomato_tart_tomatoes = self.env.ref(
            "mrp_food.demo_bom_tomato_tart_line_tomatoes"
        )

    def test_01_bom_price_subtotal_line(self):
        self.assertEqual(
            self.bom_tomato_tart_tomatoes.standard_price_subtotal,
            1.5,
        )
        self.bom_tomato_tart_tomatoes.product_qty = 1
        self.assertEqual(
            self.bom_tomato_tart_tomatoes.standard_price_subtotal,
            3,
        )

    def test_02_bom_price_total(self):
        self.assertEqual(
            self.bom_tomato_tart.standard_price_total,
            6.7,
        )
        self.bom_tomato_tart.write({"bom_line_ids": [(5, 0)]})
        self.assertEqual(
            self.bom_tomato_tart.standard_price_total,
            0,
        )
