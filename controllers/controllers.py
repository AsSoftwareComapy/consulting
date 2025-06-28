# -*- coding: utf-8 -*-
# from odoo import http


# class consulting(http.Controller):
#     @http.route('/consulting/consulting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/consulting/consulting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('consulting.listing', {
#             'root': '/consulting/consulting',
#             'objects': http.request.env['consulting.consulting'].search([]),
#         })

#     @http.route('/consulting/consulting/objects/<model("consulting.consulting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('consulting.object', {
#             'object': obj
#         })

