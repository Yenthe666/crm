# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sales_team_default_stage_ids = fields.Many2many(
        'crm.stage',
        related='company_id.sales_team_default_stage_ids',
        readonly=False,
        string="Default sales team stages"
    )
