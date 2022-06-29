# -- coding: utf-8 --
from odoo import models, fields, api
from datetime import timedelta
from datetime import date


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def send_email_reminder(self):
        """
        Search all leads that are in a stage that is configured for reminders.
        Then send out the reminder if it is the correct day.
        """
        stages_with_reminder = self.env['crm.stage'].search([
            ('lead_mail_rule_ids', '!=', False)
        ])

        leads = self.env['crm.lead'].search([('stage_id', 'in', stages_with_reminder.ids)])

        today = date.today()

        for lead in leads:
            for lead_rule in lead.stage_id.lead_mail_rule_ids.filtered(lambda rule: rule.active):
                reminder_day = lead_rule.send_reminder_after
                new_reminder_date = (lead.date_last_stage_update + timedelta(reminder_day)).date()
                if new_reminder_date == today:
                    lead_rule.email_template_id.use_default_to = True
                    lead.with_context(lang=lead.partner_id.lang).message_post_with_template(
                        lead_rule.email_template_id.id,
                        email_layout_xmlid="mail.mail_notification_light"
                    )
