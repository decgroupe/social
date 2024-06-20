# Copyright 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import functools

import dateutil.relativedelta as relativedelta
from werkzeug import urls

from odoo import fields, models
from odoo.tools import safe_eval

# functions dict define by Odoo 17.0 in odoo/tools/rendering_tools.py and quite
# similar to Odoo 14.0 jinja environnement initialization `jinja_template_env` from
# odoo/addons/mail/models/mail_render_mixin.py
template_env_globals = {
    "str": str,
    "quote": urls.url_quote,
    "urlencode": urls.url_encode,
    "datetime": safe_eval.datetime,
    "len": len,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "filter": filter,
    "reduce": functools.reduce,
    "map": map,
    "relativedelta": relativedelta.relativedelta,
    "round": round,
    "hasattr": hasattr,
}


class MailTemplate(models.Model):
    _inherit = "mail.template"

    body_type = fields.Selection(
        [("jinja2", "Jinja2"), ("qweb", "QWeb")],
        "Body templating engine",
        default="jinja2",
        required=True,
    )
    body_view_id = fields.Many2one("ir.ui.view", domain=[("type", "=", "qweb")])
    body_view_arch = fields.Text(related="body_view_id.arch")

    def _render_qweb_body_eval_context(self, record):
        render_context = self._render_qweb_eval_context()
        render_context.update(template_env_globals)
        render_context.update(
            {
                "object": record,
                "email_template": self,
                "company": self.env.user.company_id,
            }
        )
        return render_context

    def _render_qweb_body(
        self, res_ids, compute_lang=False, set_lang=False, post_process=False
    ):
        self.ensure_one()
        if compute_lang:
            templates_res_ids = self._classify_per_lang(res_ids)
        elif set_lang:
            templates_res_ids = {set_lang: (self.with_context(lang=set_lang), res_ids)}
        else:
            templates_res_ids = {self._context.get("lang"): (self, res_ids)}
        res = {}
        rendered_templates = {}
        for _lang, (template, tpl_res_ids) in templates_res_ids.items():
            for res_id in tpl_res_ids:
                record = template.env[template.model].browse(res_id)
                values = template._render_qweb_body_eval_context(record)
                rendered_templates[res_id] = template.body_view_id._render(values)
            if post_process:
                rendered_templates = self._render_template_postprocess(
                    rendered_templates
                )
            for res_id, rendered in rendered_templates.items():
                res[res_id] = rendered
        return res

    def _render_field(
        self, field, res_ids, compute_lang=False, set_lang=False, post_process=False
    ):
        if self.body_type == "qweb" and field == "body_html":
            res = self._render_qweb_body(
                res_ids,
                compute_lang=compute_lang,
                set_lang=set_lang,
                post_process=post_process,
            )
        else:
            res = super()._render_field(
                field=field,
                res_ids=res_ids,
                compute_lang=compute_lang,
                set_lang=set_lang,
                post_process=post_process,
            )
        return res
