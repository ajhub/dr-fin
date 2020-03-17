#!/usr/bin/python2.7

""" Main module
"""

import webapp2

from hanlder.dialog_flow_fulfillment_handler import DialogFlowFulfillmentHandler
from hanlder.user_data_handler import UserDataHandler
app = webapp2.WSGIApplication([
                               ('/dialog-flow-fulfillment', DialogFlowFulfillmentHandler),
                               ('/user_data', UserDataHandler),
                               ])
