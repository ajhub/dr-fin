from google.appengine.ext import ndb
import config

class User(ndb.Expando):
    name = ndb.StringProperty()
    date_of_birth = ndb.DateTimeProperty()
    per_month_salary = ndb.IntegerProperty(default=0)
    per_month_rent = ndb.IntegerProperty(default=0)
    per_month_investment = ndb.IntegerProperty(default=0)
    per_month_emi = ndb.IntegerProperty(default=0)
    per_month_expenses = ndb.IntegerProperty(default=0)
    no_of_dependents = ndb.IntegerProperty(default=0)
    only_earning_member = ndb.BooleanProperty(default=True)
    create_date = ndb.DateProperty(auto_now=True)

class PassiveIncome(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)
    start_date = ndb.DateTimeProperty(required=True)
    amount = ndb.IntegerProperty()
    passive_income_class = ndb.StringProperty(choices=config.PASSIVE_INCOME_CLASS)
    create_date = ndb.DateTimeProperty(auto_now=True)

class Debt(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)
    start_date = ndb.DateTimeProperty(required=True)
    amount = ndb.IntegerProperty()
    debt_class = ndb.StringProperty(choices=config.LOAN_CLASS)
    interest_rate = ndb.IntegerProperty()
    tenure_in_months = ndb.IntegerProperty()
    create_date = ndb.DateTimeProperty(auto_now=True)


class Insurance(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)
    start_date = ndb.DateTimeProperty(required=True)
    end_date = ndb.DateTimeProperty(required=True)
    premium = ndb.IntegerProperty()
    coverage = ndb.IntegerProperty()
    insurance_class = ndb.StringProperty(choices=config.INSURANCE_CLASS)
    return_of_interest = ndb.IntegerProperty(default=0)
    create_date = ndb.DateTimeProperty(auto_now=True)


class Investment(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)
    start_date = ndb.DateTimeProperty(required=True)
    amount = ndb.IntegerProperty()
    tenure = ndb.IntegerProperty()
    investment_class = ndb.StringProperty(choices=config.INVESTMENT_CLASS)
    return_on_investment = ndb.IntegerProperty()
    create_date = ndb.DateTimeProperty(auto_now=True)


class Assets(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)
    asset_date = ndb.DateTimeProperty(required=True)
    amount = ndb.IntegerProperty()
    asset_class = ndb.StringProperty(choices=config.ASSET_CLASS)
    create_date = ndb.DateTimeProperty(auto_now=True)

class Transactions(ndb.Expando):
    user = ndb.KeyProperty(User, required=True)

    class_name = ndb.StringProperty()
    sub_class_name = ndb.StringProperty()
    class_id = ndb.StringProperty()
    create_date = ndb.DateTimeProperty(auto_now=True)
    amount = ndb.IntegerProperty()