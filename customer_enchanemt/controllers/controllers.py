# -*- coding: utf-8 -*-
# from odoo import http


# class CustomerEnchanemt(http.Controller):
#     @http.route('/customer_enchanemt/customer_enchanemt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_enchanemt/customer_enchanemt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_enchanemt.listing', {
#             'root': '/customer_enchanemt/customer_enchanemt',
#             'objects': http.request.env['customer_enchanemt.customer_enchanemt'].search([]),
#         })

#     @http.route('/customer_enchanemt/customer_enchanemt/objects/<model("customer_enchanemt.customer_enchanemt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_enchanemt.object', {
#             'object': obj
#         })

