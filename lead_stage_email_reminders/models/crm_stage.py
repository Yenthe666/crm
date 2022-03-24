# -- coding: utf-8 --
from odoo import models, fields, _
from odoo.exceptions import UserError


class CrmStage(models.Model):
    _inherit = "crm.stage"

    lead_mail_rule_ids = fields.One2many(
        comodel_name='lead.mail.rule',
        inverse_name='stage_id',
        string="Mail rules",
        context={'active_test':False}
    )

    def unlink(self):
        for record in self:
            if record.lead_mail_rule_ids:
                raise UserError(_('There are e-mail reminder rules configured for this stage. Please remove them or change them so they belong to another stage first.'))
        super(CrmStage, self).unlink()
