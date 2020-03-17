import logging
import config
import webapp2
import json
from config import set_response
from datastore import User
from fin_health import FinHealth
from lib.calculation import *
from datetime import timedelta
from lib.recommendation_engine import RecommendationEngine

class DialogFlowFulfillmentHandler(webapp2.RequestHandler):
    def _options(self):
        config.set_options_header(self.response.headers)

    def get(self):
        pass

    def post(self):
        #logging.info(self.request)

        response_payload = {}
        req_body = self.request.body
        self.df_query_obj = json.loads(req_body)
        logging.info(self.df_query_obj)

        intent = self.df_query_obj.get("queryResult").get("intent").get("displayName")

        if intent == "net-worth":
            response_payload = self.handle_net_worth_intent()
        elif intent == "net-worth-detailed":
            response_payload = self.handle_net_worth_detailed_intent()
        elif intent == "recommend-actions":
            response_payload = self.handle_recommend_actions_intent()
        elif intent == "overall-fin-health":
            response_payload = self.handle_overall_fin_health_intent()

        set_response(200, response_payload, self.response)

    def delete(self):
        pass

    def put(self):
        pass

    def get_params_from_context_objects(self, param_name):

        query_result = self.df_query_obj.get("queryResult")
        output_contexts = query_result.get("outputContexts")
        for o_c in output_contexts:

            logging.info(o_c.get("parameters"))
            if o_c.get("parameters") and o_c.get("parameters").get(param_name):
                return o_c.get("parameters").get(param_name)

    def find_user_name_and_load_user(self):

        user_name = self.get_params_from_context_objects("user_name")

        self.load_user_obj(user_name)
        logging.info(self.user_obj)

    def handle_net_worth_intent(self):

        self.find_user_name_and_load_user()

        if self.user_obj:

            response_payload = {}

            years_from_now = self.get_params_from_context_objects("years_from_now")

            if years_from_now:
                years_from_now = int(years_from_now)
                logging.info("years_from_now" + str(int(years_from_now)))

                date_target = datetime.now() + timedelta(days=int(years_from_now) * 365)
                worth_details_in_future = calculate_value_in_future(self.user_obj.key.id(), date_target)
                response_payload["fulfillmentText"] = self.user_obj.name.capitalize() + ", Your net worth " + \
                                                      str(years_from_now) + " years from now would be " + str(worth_details_in_future.get("net_worth"))

            else:
                asset_value = calculate_asset_value(self.user_obj.key.id())
                debt_value = calculate_debt_value(self.user_obj.key.id())
                investment_details = calculate_investment_value(self.user_obj.key.id())

                net_worth = asset_value['total_asset'] + investment_details['total_investment'] - debt_value[
                    'total_liability']

                response_text = self.user_obj.name.capitalize() + ", Your net worth right now stands at " + str(
                    net_worth)
                response_payload["fulfillmentText"] = response_text

            return response_payload

    def handle_net_worth_detailed_intent(self):

        self.find_user_name_and_load_user()

        if self.user_obj:

            asset_value = calculate_asset_value(self.user_obj.key.id())
            debt_value = calculate_debt_value(self.user_obj.key.id())
            investment_details = calculate_investment_value(self.user_obj.key.id())

            response_payload = {}
            response_text = self.user_obj.name.capitalize() + ", Your cash reserve, assets and investments add up to " + str(asset_value['total_asset'] + investment_details['total_investment'])
            response_text += ". Your total debts right now are " + str(debt_value['total_liability'])
            response_payload["fulfillmentText"] = response_text

            return response_payload

    def handle_recommend_actions_intent(self):

        self.find_user_name_and_load_user()

        if self.user_obj:
            response_payload = {}
            response_text = ""

            re_obj = RecommendationEngine(user_id=self.user_obj.key.id())
            recommendations = re_obj.get_overall_recommendations()

            if len(recommendations) == 0:
                response_text = "Congratulations! You have been managing your finances well. Go take that vacation :D "
            else:
                for r in recommendations:
                    response_text += r

            response_payload["fulfillmentText"] = response_text

            return response_payload

    def handle_overall_fin_health_intent(self):

        self.find_user_name_and_load_user()

        if self.user_obj:
            response_payload = {}
            response_payload["fulfillmentText"] = "I'll be soon able to tell your financial health. Give me some time."


            return response_payload

    def load_user_obj(self, user_name):

        logging.info("Trying to load user with user name - " + user_name.lower())
        self.user_obj = User.query(User.name == user_name.lower()).get()