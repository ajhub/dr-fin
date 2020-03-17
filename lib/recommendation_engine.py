from datastore import *
from google.appengine.ext import ndb
import logging
from datetime import datetime
from lib.calculation import *
from config import *

class RecommendationEngine(object):

    def __init__(self, user_id):

        self.user_obj = User.get_by_id(user_id)
        self.user_id = self.user_obj.key.id()

    def get_overall_recommendations(self):

        # LEVEL 1
        # EMERGENCY FUNDS
        emergency_fund_health_details = self.evaluate_emergency_funds_health()

        all_recommendations = []
        all_recommendations.extend(emergency_fund_health_details["recommendations"])

        return all_recommendations

    def evaluate_emergency_funds_health(self):

        health_details = {
            "alerts": {},
            "recommendations": []
        }

        asset_details_cash = calculate_asset_value(user_id=self.user_id, filter_class=config.CASH)
        total_cash_available = asset_details_cash.get("total_asset")

        if total_cash_available < self.user_obj.per_month_salary * 3:
            health_details["alerts"]["emergency_fund_alert"] = True

            recommendation = "You do not have enough liquid holdings for emergency funds. "
            recommendation += "Your liquid holdings right now are " + str(total_cash_available) + \
                              ". We suggest that you should atleast have " + str(
                self.user_obj.per_month_salary * 3) + " (3 months of salary). "

            health_details["recommendations"].append(recommendation)

        logging.info("emergency_fund_health_details" + str(health_details))
        return health_details

    def evaluate_bad_loans(self):
        debt_info = calculate_debt_value(self.user_id, checkpoint=datetime.now())
        total_bad = 0

        bad_loans_health = {
            "alerts": {},
            "recommendations": []
        }

        for debt in debt_info['liability_details']:
            if debt['class'] != config.HOME_LOAN and debt['debt_amount'] != 0:
                total_bad += debt['debt_amount']

        if total_bad > 0:
            bad_loans_health["alerts"]["bad_loan_alert"] = True

            recommendation = "You have a bad loan outstanding which is not contributing towards your goals."
            recommendation += "Your outstanding right now are " + str(total_bad) + \
                              ". We suggest that you should settle this bad loan prior as soon as possible."

            bad_loans_health["recommendations"].append(recommendation)

        return bad_loans_health

    def evaluate_medicle_insurance_health(self):
        insurances = Insurance.query(Insurance.user == ndb.Key(User, self.user_id),
                                     Insurance.insurance_class.IN(config.MEDICAL_INSURANCE))

        total_cover = 0
        shortfall = 0
        user_obj = User.get_by_id(self.user_id)

        medical_insurance_health = {
            "alerts": {},
            "recommendations": []
        }

        no_of_dependents = self.user_obj.no_of_dependents

        for insurance in insurances:
            total_cover += insurance.coverage

        if total_cover == 0:
            medical_insurance_health["alerts"]["medical_insurance_alert"] = True
            recommendation = "You do not have a medical insurance for your{}.".format(
                "self" if not no_of_dependents else " family")
            recommendation += "Your should have a health cover of atleast {}.".format(str(shortfall))

            medical_insurance_health["recommendations"].append(recommendation)
            return medical_insurance_health

        if no_of_dependents == 0:
            if total_cover < user_obj.per_month_salary/2.0 * 6 * user_obj.no_of_dependents:
                shortfall = user_obj.per_month_salary/2.0 * 6 * user_obj.no_of_dependents - total_cover
        else:
            if total_cover < user_obj.per_month_salary * 6 * user_obj.no_of_dependents:
                shortfall = user_obj.per_month_salary * 6 * user_obj.no_of_dependents - total_cover


        if shortfall:
            medical_insurance_health["alerts"]["medical_insurance_alert"] = True
            recommendation = "You are short of a sufficient health cover for your{}.".format( "self" if not no_of_dependents else " family" )
            recommendation += "Your should increase your health cover by {}.".format(str(shortfall))

            medical_insurance_health["recommendations"].append(recommendation)

        return  medical_insurance_health

    def evaluate_life_insurance_health(self):
        insurances = Insurance.query(Insurance.user == ndb.Key(User, self.user_id),
                                     Insurance.insurance_class.IN(config.LIFE_INSURANCE,config.LIFE_INSURANCE_WITH_RETURN))

        total_cover = 0
        shortfall = 0
        user_obj = User.get_by_id(self.user_id)

        life_insurance_health = {
            "alerts": {},
            "recommendations": []
        }

        for insurance in insurances:
            total_cover += insurance.coverage

        if total_cover < user_obj.per_month_salary * 120 and self.user_obj.no_of_dependents:
            shortfall = user_obj.per_month_salary * 120 - total_cover

        if shortfall:
            life_insurance_health["alerts"]["medical_insurance_alert"] = True
            recommendation = "You are short of a sufficient life cover for your family."
            recommendation += "Your should increase your life cover by {}.".format(str(shortfall))

            life_insurance_health["recommendations"].append(recommendation)

    def evaluate_car_purchase(self):
        total_life_shortfall = self.evaluate_life_insurance_health()
        total_medical_shortfall = self.evaluate_medicle_insurance_health()
        total_bad_loan = self.evaluate_bad_loans()
        emergency_fund = self.evaluate_emergency_funds_health()

        car_purchase_health = {
            "alerts": {},
            "recommendations": []
        }

        alerts = {}

        alerts.\
            update(total_medical_shortfall['alerts']).\
            update(total_life_shortfall['alerts']).\
            update(total_bad_loan['alerts']).\
            update(emergency_fund['alerts'])

        recommendations = total_life_shortfall['recommendations'] \
                          + total_medical_shortfall['recommendations'] \
                          + total_bad_loan['recommendations'] + \
                          emergency_fund['recommendations']

        if len(recommendations) == 0:
            car_value = 0
            month_spare_cash = calculate_monthly_spare(self.user_id)

            if ( month_spare_cash > 0 and month_spare_cash < 6000):
                car_purchase_health['alerts']['car_purchase_health'] = True
                recommendation = "With your current income, expenses, emis and investment, you save a cash reserve of {} per month".format(str(month_spare_cash))
                recommendation += "We would not recommend you to commit to a car with such cash reserve levels. If need be, please go for a bike."

            else:
                emi_capacity = 0.75*month_spare_cash
                loan_amount = emi_capacity * 60 / (1 + 0.08 * 5)

                recommendation = "Your monthly cash savings allow you to avail a loan of {} at an emi of {} per month".format(
                    str(loan_amount), str(emi_capacity))

                asset_details_cash = calculate_asset_value(user_id=self.user_id, filter_class=config.CASH)
                total_cash_available = asset_details_cash.get("total_asset")

                total_cash_for_downpayment = total_cash_available * 0.5
                car_price = loan_amount + total_cash_for_downpayment

                recommendation += "With your cash reserves level, we suggest you to make a down payment of not more than {}".format(str(total_cash_for_downpayment))
                recommendation += "Hence, you can buy a car worth {}".format(str(car_price))

                car_purchase_health['recommendations'].append(recommendation)

        return car_purchase_health

