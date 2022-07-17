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

    lead_ids = fields.Many2many(
        comodel_name='crm.lead',
        string='Leads'
    )

    def action_view_leads(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.lead_ids.ids)],
            'name': 'Leads with new reminder sent'
        }

    def action_send_reminders(self):
        """
        Send reminders to the leads
        """
        stages_with_reminder = self.env['crm.stage'].search([
            ('lead_mail_rule_ids', 'in', self.with_context(active_test=False).lead_mail_rule_ids.ids)
        ])
        leads = self.env['crm.lead'].search([('stage_id', 'in', stages_with_reminder.ids)])
        today = date.today()
        lead_reminders_sent = []
        for lead in leads:
            for lead_rule in lead.stage_id.lead_mail_rule_ids:
                reminder_day = lead_rule.send_reminder_after
                new_reminder_date = (lead.date_last_stage_update + timedelta(reminder_day)).date()
                if new_reminder_date <= today:
                    lead_rule.email_template_id.use_default_to = True
                    lead.with_context(lang=lead.partner_id.lang).message_post_with_template(
                        lead_rule.email_template_id.id,
                        email_layout_xmlid="mail.mail_notification_light"
                    )
                    lead_reminders_sent.append(lead)
        feedback = _('Reminders were sent to the following leads:\n')
        for lead in lead_reminders_sent:
            feedback += f'\n{lead.name}'
        self.write({
            'feedback': feedback,
            'state': 'done',
            'lead_ids': [(6, 0, [l.id for l in lead_reminders_sent])]
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.mail.reminder.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'name': 'Lead email reminders sent'
        }
