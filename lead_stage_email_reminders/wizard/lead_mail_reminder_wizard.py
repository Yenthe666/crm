# -- coding: utf-8 --
from datetime import date, timedelta

from odoo import models, fields, api, _


class LeadMailReminderWizard(models.TransientModel):
    _name = "lead.mail.reminder.wizard"
    _description = "Lead Email Reminder wizard"

    state = fields.Selection(
        selection=[
            ('start', 'Start'),
            ('done', 'Done')
        ],
        default='start'
    )

    team_ids = fields.Many2many(
        comodel_name='crm.team',
        string='Sales teams',
        required=True
    )

    lead_mail_rule_ids = fields.Many2many(
        comodel_name='lead.mail.rule',
        domain="[('team_id', 'in', team_ids), '|', ('active', '=', True), ('active', '=', False)]",
        string='Mail rules',
        required=True
    )

    feedback = fields.Text(
        string='Feedback'
    )

    valid_stage_ids = fields.Many2many(
        comodel_name='crm.stage',
        string='Valid stages'
    )

    lead_ids = fields.Many2many(
        comodel_name='crm.lead',
        string='Leads',
        domain="[('stage_id', 'in', valid_stage_ids)]"
    )

    def action_view_leads(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.lead_ids.ids)],
            'name': 'Leads with new reminder sent'
        }

    @api.onchange('lead_mail_rule_ids')
    def get_leads_for_reminder(self):
        """
        Get all leads for reminders
        """
        leads_to_remove = self.env['crm.lead']
        for lead in self.lead_ids:
            if lead.team_id not in self.team_ids:
                leads_to_remove += lead

        self.lead_ids -= leads_to_remove

        stages_with_reminder = self.env['crm.stage'].search([
            ('lead_mail_rule_ids', 'in', self.with_context(active_test=False).lead_mail_rule_ids.ids)
        ])
        leads = self.env['crm.lead'].search([('stage_id', 'in', stages_with_reminder.ids)])
        today = date.today()
        for lead in leads:
            for lead_rule in lead.stage_id.lead_mail_rule_ids:
                reminder_day = lead_rule.send_reminder_after
                new_reminder_date = (lead.date_last_stage_update + timedelta(reminder_day)).date()
                if new_reminder_date <= today:
                    self.lead_ids += lead

        # Set valid stages for selecting leads
        self.valid_stage_ids = self.lead_mail_rule_ids.stage_id

    def action_send_reminders(self):
        """
        Send reminders to the leads
        """
        for lead in self.lead_ids:
            for lead_rule in lead.stage_id.lead_mail_rule_ids:
                lead_rule.email_template_id.use_default_to = True
                lead.with_context(lang=lead.partner_id.lang).message_post_with_template(
                    lead_rule.email_template_id.id,
                    email_layout_xmlid="mail.mail_notification_light"
                )
        feedback = _('Reminders were sent to the following leads:\n')
        for lead in self.lead_ids:
            feedback += f'\n{lead.name}'
        self.write({
            'feedback': feedback,
            'state': 'done',
            'lead_ids': [(6, 0, self.lead_ids.ids)]
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.mail.reminder.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'name': _('Lead email reminders sent')
        }
