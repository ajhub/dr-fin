from datastore import *
from google.appengine.ext import ndb
import logging
from datetime import datetime

def calc_value(amount, time, roi):
    return int(amount + (amount * (roi / 36500.0) * time))

def calc_recuuring_value(amount, time, roi, compounding_in_one_year=4):
    total = 0
    time_months = time/30

    for i in range(time_months):
        total += (amount * (1 + (roi/(100.0*compounding_in_one_year)))**(i*compounding_in_one_year/12))
    return int(total)

def calculate_asset_value(user_id, filter_class=None, checkpoint=datetime.now()):
    asset_value = []

    if filter_class is None:
        assets = Assets.query(Assets.user == ndb.Key(User, user_id)).fetch()
    else:
        assets = Assets.query(Assets.user == ndb.Key(User, user_id), Assets.asset_class == filter_class).fetch()

    for asset in assets:
        value = calc_value(asset.amount, (checkpoint - asset.asset_date).days, config.ASSET_ROI[asset.asset_class])
        asset_value.append(dict({"class": asset.asset_class, "amount": value}))

    total_asset = sum([record['amount'] for record in asset_value])
    return {
        'total_asset' : int(total_asset),
        'asset_details' : asset_value
    }


def calc_outstanding_debt(amount, interest, tenure, start_date, checkpoint=datetime.now()):
    total_laibility = amount + amount * interest / 1200 * tenure
    total_months = int((checkpoint - start_date).days / 30)

    per_month_emi = total_laibility / tenure
    total_paid = per_month_emi * total_months

    return max(int(total_laibility - total_paid),0), max(tenure - total_months,0)

def calculate_debt_value(user_id, filter_class=None, checkpoint=datetime.now()):
    debt_value = []
    if filter_class is None:
        debts = Debt.query(Debt.user == ndb.Key(User, user_id)).fetch()
    else:
        debts = Debt.query(Debt.user == ndb.Key(User, user_id), Debt.debt_class == filter_class).fetch()

    for debt in debts:
        amount = debt.amount
        interest = debt.interest_rate
        tenure = debt.tenure_in_months
        debt_class = debt.debt_class
        start_date = debt.start_date
        outstanding_amount, months_left = calc_outstanding_debt(amount, interest, tenure, start_date, checkpoint)
        debt_value.append(dict({
            "class": debt_class,
            "debt_amount": outstanding_amount,
            "tenure": months_left
        }))

    total_liability = sum([record['debt_amount'] for record in debt_value])
    return {
        'total_liability' : total_liability,
        'liability_details' : debt_value
    }

def calculate_investment_value(user_id, filter_class=None, checkpoint=datetime.now()):
    if filter_class is None:
        investments = Investment.query(Investment.user == ndb.Key(User, user_id)).fetch()
    else:
        investments = Investment.query(Investment.user == ndb.Key(User, user_id), Investment.debt_class == filter_class).fetch()

    investment_value = []
    for investment in investments:
        amount = investment.amount
        tenure = investment.tenure
        roi = investment.return_on_investment

        if investment.investment_class == config.SIP_INVESTMENT:
            value = calc_recuuring_value(amount, (checkpoint - investment.start_date).days, roi, compounding_in_one_year=12)
        else:
            value = calc_value(amount, (checkpoint - investment.start_date).days, roi)
        logging.info(value)
        time_to_maturity = max ( int (tenure - (checkpoint - investment.start_date).days / 30), 0)

        investment_value.append(dict({"class": investment.investment_class, "value_today": value, "time_to_mature" : time_to_maturity}))

    total_investment_value = sum([record['value_today'] for record in investment_value])

    return {
        'total_investment': total_investment_value,
        'investment_details': investment_value
    }


def calculate_value_in_future(user_id, future_date):
    today = datetime.now()

    total_months = int((future_date - today).days/30)
    total_years = int(round(total_months/12.0))
    user_obj = User.get_by_id(user_id)

    total_salary_year = 12 * user_obj.per_month_salary
    total_salary_in_tenure = 0

    for i in range(total_years):
        total_salary_in_tenure += total_salary_year * ((1 + 0.1)**(i+1))

    total_expenses_year = 12 * user_obj.per_month_expenses
    total_expenses_in_tenure = 0

    for i in range(total_years):
        total_expenses_in_tenure += total_expenses_year * ((1 + 0.06)**(i+1))

    total_rent = 12 * user_obj.per_month_rent
    total_rent_in_tenure = 0

    for i in range(total_years):
        total_rent_in_tenure += total_rent * ((1 + 0.1)**(i+1))

    investment_dict = calculate_investment_value(user_id, checkpoint=future_date)
    total_outstanding = calculate_debt_value(user_id, checkpoint=today)['total_liability']
    debt_details = calculate_debt_value(user_id, checkpoint=future_date)

    asset_that_day = calculate_asset_value(user_id, checkpoint=future_date)

    monthly_investment = 0
    investment_records = Investment.query(Investment.user == ndb.Key(User, user_id)).fetch()

    for investment in investment_records:
        if investment.investment_class == config.SIP_INVESTMENT:
            monthly_investment += investment.amount

    total_invested = total_months * monthly_investment
    total_taxes = 0

    total_cash_reserve = total_salary_in_tenure - total_rent_in_tenure - total_invested - total_taxes - total_outstanding - total_expenses_in_tenure

    asset_that_day['asset_details'].append(dict({'amount': total_cash_reserve, 'class': config.CASH}))
    asset_that_day['total_asset'] += total_cash_reserve


    answer_dict = {
                'total_asset' : asset_that_day['total_asset'],
                'total_liability' : debt_details['total_liability'],
                'total_investment' : investment_dict['total_investment'],
                'asset_details' : asset_that_day['asset_details'],
                'liability_details' : debt_details['liability_details'],
                "investment_details" : investment_dict['investment_details'],
                'net_worth' : asset_that_day['total_asset'] + investment_dict['total_investment'] - debt_details['total_liability']
            }

    return answer_dict


def calculate_monthly_spare(user_id, ):
    today = datetime.now()
    user_obj = User.get_by_id(user_id)

    total_salary = 12 * user_obj.per_month_salary
    total_expenses = user_obj.per_month_expenses
    total_rent = user_obj.per_month_rent

    monthly_investment = 0
    investment_records = Investment.query(Investment.user == ndb.Key(User, user_id)).fetch()

    for investment in investment_records:
        if investment.investment_class == config.SIP_INVESTMENT:
            monthly_investment += investment.amount

    total_outstanding = calculate_debt_value(user_id, checkpoint=today)['total_liability']
    per_month_emi = sum(record['debt_amount']/record['tenure'] if record['tenure'] else 0 for record in total_outstanding)

    total_cash_reserve = total_salary - total_rent - monthly_investment - per_month_emi  - total_outstanding - total_expenses

    return total_cash_reserve