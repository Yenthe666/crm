# -*- coding: utf-8 -*-
from odoo import fields, models, _


class CrmTeamStageWizard(models.TransientModel):
    _name = "crm.team.stage.wizard"

    state = fields.Selection(
        selection=[
            ('start', 'Start'),
            ('done', 'Done')
        ],
        default='start'
    )

    name = fields.Char(
        string='Stage name',
        required=True
    )

    action = fields.Selection(
        selection=[
            ('delete', 'Delete'),
            ('create', 'Create')
        ],
        string='Action',
        required=True
    )

    crm_team_ids = fields.Many2many(
        comodel_name='crm.team',
        string='Sales teams',
        default=lambda self: self._get_default_teams(),
        required=True
    )

    feedback = fields.Text(
        string='Feedback'
    )

    def _get_default_teams(self):
        return self.env['crm.team'].search([]).ids

    def action_delete(self):
        """
        Delete the stages for the selected sales teams
        """
        # Look for all stages that must be deleted
        stages_to_delete = self.env['crm.stage'].search([
            ('name', '=', self.name),
            ('team_id', 'in', self.crm_team_ids.ids)
        ])
        # Search for leads that are in a stage that will be deleted
        leads = self.env['crm.lead'].search([('stage_id', 'in', stages_to_delete.ids)])
        # If there are any leads, display their name in the wizard so the stage on those leads can be changed
        if leads:
            self.write({
                'feedback': _('There are still leads that have the stage %s.\nPlease change the stage of these leads first.\n\n') % self.name + f"\n{team.name}" for team in leads
            })
            return self.return_wizard()

        # Remove the stages
        stages_to_delete.unlink()
        # Give feedback that all stages were removed
        self.write({
            'feedback': _('The stage %s was successfully removed from the selected sales teams.') % self.name,
            'state': 'done'
        })
        return self.return_wizard()

    def action_create(self):
        """
        Create the stages for the selected sales teams
        """
        # Look for stages that already exist with the given name
        existing_stages = self.env['crm.stage'].search([
            ('name', '=', self.name),
            '|',
            ('team_id', 'in', self.crm_team_ids.ids),
            ('team_id', '=', False)
        ])
        if existing_stages:
            # If there are any stages with the given name and for one of the selected sales teams, return a message that the stage already exists for certain teams.
            teams_with_existing_stage = existing_stages.team_id
            if teams_with_existing_stage:
                self.write({
                    'feedback': _('The following sales teams already have a stage named %s:\n\n') % self.name + f"\n{team.name}" for team in teams_with_existing_stage
                })
                return self.return_wizard()
            # If there are existing stages with the given name, but without a team, return a message that this stage already exists.
            self.write({
                'feedback': _('The stage %s already exists as a default stage.') % self.name
            })
            return self.return_wizard()

        # Create all the stages
        for team in self.crm_team_ids:
            self.env['crm.stage'].create({
                'name': self.name,
                'team_id': team.id
            })
        self.write({
            'feedback': _('The stage %s was successfully created for the selected sales teams.') % self.name,
            'state': 'done'
        })
        return self.return_wizard()

    def return_wizard(self):
        """
        Return to the wizard
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.team.stage.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'name': 'Update sales team stages'
        }