from datastore import User
import logging

from datetime import datetime


class UserClass(object):
    def __init__(self, user_id):
        if user_id is None:
            self.user_object = User.get_by_id(user_id)
        else:
            if not isinstance(user_id, str):
                raise ValueError("UserID should be string")

            try:
                self.user_object = User.get_by_id(user_id)
                if self.user_object is None:
                    logging.warning("User not found, creating new user")
                    self.user_object = User(id=user_id)
                    self.user_object.put()


            except Exception as e:
                logging.error("Something wient wrong : {}".format(e))
                raise Exception

        self.userid = self.user_object.key.id()


    def set_name(self, name):
        if not isinstance(name , str):
            raise TypeError
        self.user_object.name = name

    def set_date_of_birth(self, date_obj):
        if not isinstance(date_obj, datetime):
            raise TypeError

        self.user_object.date_of_birth = date_obj

    def set_per_month_salary(self, per_month_salary):
        if not isinstance(per_month_salary, int):
            raise TypeError

        self.user_object.per_month_salary = per_month_salary

    def set_per_month_rent(self, per_month_rent):
        if not isinstance(per_month_rent, int):
            raise TypeError

        self.user_object.per_month_rent = per_month_rent

    def set_per_month_investment(self, per_month_investment):
        if not isinstance(per_month_investment, int):
            raise TypeError

        self.user_object.per_month_investment = per_month_investment

    def set_per_month_expenses(self, per_month_expenses):
        if not isinstance(per_month_expenses, int):
            raise TypeError

        self.user_object.per_month_expenses = per_month_expenses

    def set_no_of_dependents(self, no_of_dependents):
        if not isinstance(no_of_dependents, int):
            raise TypeError

        self.user_object.no_of_dependents = no_of_dependents

    def set_only_earning_member(self, only_earning_member):
        if not isinstance(only_earning_member, int):
            raise TypeError

        self.user_object.only_earning_member = only_earning_member

    def save_data(self):
        self.user_object.put()

    def update_user(self, name, dob, salary, rent, expenses, dependents, is_only_earning):
        self.set_name(name)
        self.set_date_of_birth(dob)
        self.set_per_month_salary(salary)
        self.set_per_month_rent(rent)
        self.set_per_month_expenses(expenses)
        self.set_no_of_dependents(dependents)
        self.set_only_earning_member(is_only_earning)

        self.save_data()