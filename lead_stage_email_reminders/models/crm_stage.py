# -- coding: utf-8 --
from odoo import models, fields


class CrmStage(models.Model):
    _inherit = "crm.stage"

    send_automatic_reminder = fields.Boolean(
        string='Send Automatic Reminder'
    )

    lead_mail_rule_ids = fields.One2many(
        comodel_name='lead.mail.rule',
        inverse_name='stage_id',
        string="Rule"
    )
