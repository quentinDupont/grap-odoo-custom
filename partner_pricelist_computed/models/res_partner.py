# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_pricelist_name = fields.Char(
        compute="_compute_partner_pricelist_name", search="_search_partner_pricelist_name"
    )

    @api.depends("property_product_pricelist")
    def _compute_partner_pricelist_name(self):
        for partner in self.filtered(lambda x : x.property_product_pricelist):
            partner.partner_pricelist_name = partner.property_product_pricelist.name

    def _search_partner_pricelist_name(self, operator, value):
        if operator == 'ilike':
            if value is not False:
                id_list = []
                partners = self.env['res.partner'].search([])
                for partner in partners:
                    if value in partner.property_product_pricelist.name:
                        id_list.append(partner.id)
                return [('id', 'in', id_list)]
            else:
                return [('id', 'in', [])]
        else:
            raise UserError(_('The field name is only searchable with "contain"''))

# TODO : ajouter sur la vue éditable mais du coup on pourra pas le modifier .. à  part si on fait le set pour le compute ?
