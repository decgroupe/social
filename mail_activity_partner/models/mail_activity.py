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
            activity.partner_id = False
            if not res_model or not res_id:
                _logger.error(
                    "Activity %d is missing a model/id " "(res_model=%s, res_id=%d)",
                    activity.id,
                    res_model,
                    res_id,
                )
                continue
            if res_model == "res.partner":
                activity.partner_id = res_id
            else:
                res_model_id = activity.env[res_model].search([("id", "=", res_id)])
                # Check for existing function as this case could happen when
                # compute is called from a hook (post_install)
                if hasattr(self, "_get_partner_field_name"):
                    partner_field_name = res_model_id._get_partner_field_name()
                else:
                    partner_field_name = "partner_id"
                if partner_field_name in res_model_id._fields:
                    partner_id = res_model_id[partner_field_name]
                    activity.partner_id = partner_id
                else:
                    activity.partner_id = None
