# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    # create new tags from seasonality
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mrp_bom_tag(company_id,name,complete_name)
        SELECT company_id,name,name FROM seasonality;
        """,
    )

    # link news tags with boms
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mrp_bom_mrp_bom_tag_rel(mrp_bom_id,mrp_bom_tag_id)
        SELECT mbom.id as bom_id, tag.id as tag_id from seasonality s
        JOIN mrp_bom_tag tag ON s.name = tag.name AND s.company_id = tag.company_id
        JOIN mrp_bom_seasonality_rel sr ON sr.seasonality_id = s.id
        JOIN mrp_bom mbom ON mbom.id = sr.mrp_bom_id;
        """,
    )
