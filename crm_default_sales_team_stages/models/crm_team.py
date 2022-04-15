# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.model
    def create(self, values):
        """
            Auto create/set stages for new sale teams (if configured)
        """
        crm_team = super().create(values)
        name = values.get("name")

        if name is not None:
            # Find all default stages configured under CRM > Configuration > Settings (stored on res.company)
            default_crm_stages = crm_team.company_id.sales_team_default_stage_ids.sorted(lambda stage: stage.sequence)
            # Get the highest existing sequence
            sequence = self.env['crm.stage'].search([], order='sequence desc', limit=1).sequence
            # If any default stages we loop over them, copy them and then set the current team it's ID on it.
            if default_crm_stages:
                for default_crm_stage in default_crm_stages:
                    sequence += 1
                    # Copy the stage and assign the correct team and add a new (unique) sequence
                    default_crm_stage.copy().write({
                        'team_id': crm_team.id,
                        'sequence': sequence
                    })
        return crm_team
