import logging
import config
import webapp2
from config import set_response
from datetime import datetime, timedelta
from datastore import *
from google.appengine.ext import ndb
from lib.user_class import UserClass
from lib.calculation import *
import json

class UserDataHandler(webapp2.RequestHandler):
    def _options(self):
        config.set_options_header(self.response.headers)

    def get(self):
        user_id = self.request.get("user_id")
        date = self.request.get("date")
        if date == "now":
            asset_value = calculate_asset_value(user_id)
            debt_value = calculate_debt_value(user_id)
            investment_details = calculate_investment_value(user_id)

            data = {
                'total_asset' : asset_value['total_asset'],
                'total_liability' : debt_value['total_liability'],
                'total_investment' : investment_details['total_investment'],
                'asset_details' : asset_value['asset_details'],
                'liability_details' : debt_value['liability_details'],
                "investment_details" : investment_details['investment_details'],
                'net_worth' : asset_value['total_asset'] + investment_details['total_investment'] - debt_value['total_liability']
            }

            logging.info(data)

        else:
            date_target = datetime.now() + timedelta(days=int(self.request.get('date', 0))*365)
            data = calculate_value_in_future(user_id, date_target)

        set_response(200, data, self.response)


    def post(self):
        try:
            body = json.loads(self.request.body)
            ###### Base Data Update
            user_id = str(body.get("user_id"))
            logging.info(user_id)
            if not user_id:
                set_response(400, "Bad Request", self.response)

            name = str(body.get("name"))
            date_of_birth = body.get("date_of_birth")
            regular_income = int(body.get("regular_income"))
            rent = int(body.get("rent"))
            monthly_expense = body.get("monthly_expense")
            no_of_dependents = int(body.get("no_of_dependents"))
            only_earning_member = bool(int(body.get("only_earning_member")))

            date_of_birth_parsed = datetime.strptime(date_of_birth, config.TIME_FORMAT )

            user_obj = UserClass(user_id=user_id)
            user_obj.update_user(name=name, expenses=monthly_expense, salary=regular_income, dob=date_of_birth_parsed,
                             dependents=no_of_dependents, is_only_earning=only_earning_member, rent=rent)


            logging.info("base info done")
            ##### Passive Income
            passive_income_array = body.get("passive_income")

            for passive_income in passive_income_array:
                passive_income_object = PassiveIncome(
                    user = ndb.Key(User, user_id),
                    start_date = datetime.strptime(passive_income['start_date'], config.TIME_FORMAT ),
                    amount=int(passive_income['amount']),
                    passive_income_class=passive_income['class_name']
                )

                passive_income_object.put()

            logging.info("passive info done")
            ##### Debt
            debt_array = body.get("debt")

            for debt in debt_array:
                debt_object = Debt(
                    user=ndb.Key(User, user_id),
                    start_date=datetime.strptime(debt['start_date'], config.TIME_FORMAT),
                    amount=int(debt['amount']),
                    debt_class=debt['class_name'],
                    tenure_in_months=debt['tenure_in_months'],
                    interest_rate=int(debt['interest_rate'])
                )

                debt_object.put()

            logging.info("debt info done")
            ##### Insurance
            insurance_array = body.get("insurance")

            for insurance in insurance_array:
                insurance_object = Insurance(
                    user=ndb.Key(User, user_id),
                    start_date=datetime.strptime(insurance['start_date'], config.TIME_FORMAT),
                    end_date=datetime.strptime(insurance['end_date'], config.TIME_FORMAT),
                    premium=int(insurance['premium']),
                    coverage=int(insurance['coverage']),
                    insurance_class=insurance['class_name'],
                    interest_rate=-100
                )

                insurance_object.put()

            logging.info("insurance info done")
            ##### Investment
            investment_array = body.get("investment")

            for investment in investment_array:
                debt_object = Investment(
                    user=ndb.Key(User, user_id),
                    start_date=datetime.strptime(investment['start_date'], config.TIME_FORMAT),
                    amount=int(investment['amount']),
                    investment_class=investment['class_name'],
                    tenure=int(investment['tenure_in_months']),
                    return_on_investment=int(investment['interest_rate'])
                )
                debt_object.put()

            logging.info("investment info done")

            ##### Asset
            asset_array = body.get("asset")

            for asset in asset_array:
                asset_object = Assets(
                    user=ndb.Key(User, user_id),
                    asset_date=datetime.strptime(asset['asset_date'], config.TIME_FORMAT),
                    amount=int(asset['amount']),
                    asset_class=asset['class_name'],
                   )

                asset_object.put()

            logging.info("asset info done")

            set_response(200, "Data Updated", self.response)


        except Exception as e:
            import traceback
            logging.error(traceback.print_exc())
            set_response(500, "Server Error : {}".format(e), self.response)


    def delete(self):
        pass

    def put(self):
        pass