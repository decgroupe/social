# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from odoo import api, fields, models


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    @api.model
    def create(self, vals):
        rec = super(MailActivityMixin, self).create(vals)
        if rec and self._activity_partner_need_update(vals):
            rec._update_activity_partner()
        return rec

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if res and self._activity_partner_need_update(vals):
            self._update_activity_partner()
        return res

    @api.model
    def _get_partner_field_name(self):
        return 'partner_id'

    @api.model
    def _activity_partner_need_update(self, vals):
        res = False
        partner_field_name = self._get_partner_field_name()
        if partner_field_name in self._fields:
            # Use set intersection to find out if the `partner_id` of
            # linked activities must be updated
            depends_fields = [partner_field_name]
            if depends_fields and (set(vals) & set(depends_fields)):
                res = True
        return res

    @api.multi
    def _update_activity_partner(self):
        partner_field_name = self._get_partner_field_name()
        for rec in self:
            partner_id = rec[partner_field_name]
            rec.activity_ids.write(
                {'partner_id': partner_id.id}
            )
