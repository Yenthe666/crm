# -- coding: utf-8 --
from odoo import models, fields, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    lead_mail_rule_ids = fields.One2many(
        comodel_name='lead.mail.rule',
        inverse_name='team_id',
        string="Lead email rules"
    )

    lead_mail_rule_count = fields.Integer(
        string='Lead email rules count',
        compute='_compute_lead_mail_rule_count'
    )

    def _compute_lead_mail_rule_count(self):
        self.lead_mail_rule_count = len(self.lead_mail_rule_ids)

    def action_view_lead_mail_rules(self):
        """
        :return: Tree view with all existing rules and context to create a new rule for the current team
        """
        return {
            "name": _("Email reminder rules"),
            "type": "ir.actions.act_window",
            "res_model": "lead.mail.rule",
            "domain": [('id', 'in', self.lead_mail_rule_ids.ids)],
            "view_type": "list",
            "view_mode": "list,form",
            "target": "current",
            "context": {
                'default_team_id': self.id,
            }
        }
