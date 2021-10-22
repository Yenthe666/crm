# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sales_team_default_stage_ids = fields.Many2many(
        'crm.stage'
    )
