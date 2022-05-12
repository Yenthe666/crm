# -*- coding: utf-8 -*-
from odoo import fields, models, _


class CrmTeamStageWizard(models.TransientModel):
    _name = "crm.team.stage.wizard"
    _description = "Team stage configuration"

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

    location = fields.Selection(
        selection=[
            ('after_last', 'After last stage'),
            ('before_first', 'Before first stage'),
            ('before', 'Before'),
            ('after', 'After')
        ],
        string='Stage location',
        default='after_last'
    )

    match_on_stage_name = fields.Char(
        string='Match on stage name'
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

        sequence = 0

        teams_without_matching_stage = self._check_teams_without_matching_stage()
        if teams_without_matching_stage:
            self.write({
                'feedback': _('The following sales teams have no stage named %s:\n\n') % self.match_on_stage_name + f"\n{team.name}" for team in teams_without_matching_stage
            })
            return self.return_wizard()

        # Create all the stages
        for team in self.crm_team_ids:
            sequence = self._get_sequence(team, sequence)
            if sequence > 0:
                self.env['crm.stage'].create({
                    'name': self.name,
                    'team_id': team.id,
                    'sequence': sequence
                })

        self.write({
            'feedback': _('The stage %s was successfully created for the selected sales teams.') % self.name,
            'state': 'done'
        })
        return self.return_wizard()

    def _check_teams_without_matching_stage(self):
        """
        Check if there are any teams that don't have a stage to match the before or after statement (location) in the wizard
        """
        if self.location not in ['before', 'after']:
            return []
        teams = []
        for team in self.crm_team_ids:
            if not self.env['crm.stage'].search_count([('name', '=ilike', self.match_on_stage_name), ('team_id', '=', team.id)]):
                teams.append(team)
        return teams

    def _get_sequence(self, team, sequence):
        """
        Get the sequence for the stage to create
        """
        # If the location is after the last existing stage, we get the highest sequence and increment with 1
        if self.location == 'after_last':
            if sequence == 0:
                sequence = self.env['crm.stage'].search([], order='sequence desc', limit=1).sequence
            return sequence + 1

        # If the location is before the first existing stage, we increment the sequence of the existing stages with the total amount of stages that will be created
        # We return the current sequence + 1
        if self.location == 'before_first':
            if sequence == 0:
                stages = self.env['crm.stage'].search([], order='sequence desc')
                total_new_stages = len(self.crm_team_ids)
                for stage in stages:
                    stage.sequence += total_new_stages
            return sequence + 1

        # If the location is after a selected stage, we increment the sequence of the existing stages after the selected stage with 1
        # We return the sequence of the selected stage + 1
        if self.location == 'after' and team:
            matching_stage = self.env['crm.stage'].search([('name', '=ilike', self.match_on_stage_name), ('team_id', 'in', [False, team.id])], limit=1)
            sequence = matching_stage.sequence
            if matching_stage:
                stages = self.env['crm.stage'].search([('sequence', '>', matching_stage.sequence), ('team_id', 'in', [team.id, False])], order='sequence desc')
                for stage in stages:
                    stage.sequence += 1
                return sequence

        # If the location is before a selected stage, we increment the sequence of the existing stages on and after the selected stage with 1
        # We return the original sequence of the selected stage
        if self.location == 'before' and team:
            matching_stage = self.env['crm.stage'].search([('name', '=ilike', self.match_on_stage_name), ('team_id', 'in', [False, team.id])], limit=1)
            sequence = matching_stage.sequence
            if matching_stage:
                stages = self.env['crm.stage'].search([('sequence', '>=', matching_stage.sequence), ('team_id', 'in', [team.id, False])], order='sequence desc')
                for stage in stages:
                    stage.sequence += 1
                return sequence
        return 0

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
