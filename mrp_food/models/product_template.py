# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    date_last_statement_price = fields.Date(
        string="Date Last Statement Price",
        related="product_variant_ids.date_last_statement_price",
        readonly=False,
    )

    is_component = fields.Boolean(
        related="product_variant_ids.is_component", default=False, readonly=False
    )
