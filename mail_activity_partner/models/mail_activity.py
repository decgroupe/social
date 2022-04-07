# Copyright 2018 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        index=True,
        compute="_compute_res_partner_id",
        store=True,
    )

    commercial_partner_id = fields.Many2one(
        related="partner_id.commercial_partner_id",
        string="Commercial Entity",
        store=True,
        related_sudo=True,
        readonly=True,
    )

    @api.depends("res_model", "res_id")
    def _compute_res_partner_id(self):
        for activity in self:
            res_model = activity.res_model
            res_id = activity.res_id
            if not res_model or not res_id:
                _logger.error(
                    "Activity %d is missing a model/id " "(res_model=%s, res_id=%d)",
                    activity.id,
                    res_model,
                    res_id,
                )
                continue
            activity.partner_id = False
            if res_model:
                if res_model == "res.partner":
                    activity.partner_id = res_id
                else:
                    res_model_id = self.env[res_model].browse(res_id)
                    if "partner_id" in res_model_id._fields and res_model_id.partner_id:
                        activity.partner_id = res_model_id.partner_id
                    else:
                        activity.partner_id = False
