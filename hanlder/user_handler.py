

""" Followup Handler
"""

import logging
import config
import webapp2


class UserHandler(webapp2.RequestHandler):
    def _options(self):
        config.set_options_header(self.response.headers)

    def get(self):
        pass

    def post(self):
        name = self.request.get('name', None)
        date_of_birth_string = self.request.get('date_of_birth', None)

        per_month_salary = int(self.request.get('per_month_salary', 0))
        per_month_rent = int(self.request.get('per_month_rent', 0))
        per_month_investment = int(self.request.get('per_month_investment', 0))
        per_month_emi = int(self.request.get('per_month_emi', 0))
        per_month_expenses = int(self.request.get('per_month_expenses', 0))
        no_of_dependents = int(self.request.get('no_of_dependents', 0))
        only_earning_member = int(self.request.get('only_earning_member', False))



    def delete(self):
        pass

    def put(self):
        pass
