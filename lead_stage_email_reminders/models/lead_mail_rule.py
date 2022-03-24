# -- coding: utf-8 --
from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError


class LeadMailRule(models.Model):
    _name = "lead.mail.rule"
    _description = "Email Reminders"
    _order = "create_date asc"

    name = fields.Char(
        string='Name',
        required=True
    )

    stage_id = fields.Many2one(
        comodel_name='crm.stage',
        string="Stage Name",
        domain="[('team_id', '=', team_id)]",
        required=True
    )

    email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Email Template",
        domain=[('model', '=', 'crm.lead')],
        required=True
    )

    send_reminder_after = fields.Integer(
        string="Send Reminder After",
        required=True
    )

    team_id = fields.Many2one(
        comodel_name='crm.team',
        string="Sales Team"
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.onchange('email_template_id')
    def _onchange_email_template_id(self):
        for rule in self:
            if not rule.name:
                rule.name = rule.email_template_id.name

    @api.constrains('send_reminder_after')
    def _constrains_send_reminder_after(self):
        for rule in self:
            if rule.send_reminder_after < 1:
                raise ValidationError(_('The reminder must be sent at least after one day.'))

    @api.constrains('stage_id')
    @api.depends('stage_id')
    def set_team_id(self):
        for rule in self:
            if rule.stage_id:
                rule.team_id = rule.stage_id.team_id
