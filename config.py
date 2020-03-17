CAR_LOAN = "car-loan"
HOME_LOAN = "home-loan"
PERSONAL_LOAN = "personal-loan"

LOAN_CLASS = [ CAR_LOAN, HOME_LOAN, PERSONAL_LOAN ]

TIME_FORMAT = "%Y-%m-%d"
MEDICAL_INSURANCE = "medical-insurance"
LIFE_INSURANCE = "life-insurance"
LIFE_INSURANCE_WITH_RETURN = "ulips"

INSURANCE_CLASS = [ MEDICAL_INSURANCE, LIFE_INSURANCE, LIFE_INSURANCE_WITH_RETURN ]

GOLD_INVESTMENT = "gold"
PROPERTY_INVESTMENT = "property"
FIXED_DEPOSIT = "fixed-deposit"
SIP_INVESTMENT = "sip"
CASH = "cash"
CAR = "car"

INVESTMENT_CLASS = [ FIXED_DEPOSIT, SIP_INVESTMENT]
ASSET_CLASS = [CAR, CASH, GOLD_INVESTMENT]

ASSET_ROI = {
    CASH : 3.5,
    GOLD_INVESTMENT : 2.5,
    CAR : -20
}

RENT_INCOME = "rent"
PASSIVE_INCOME_CLASS = [RENT_INCOME]

HTTP_RESPONSE_CONTENT_TYPE = "application/json; charset=utf-8"


def set_options_header(response_headers):
    response_headers.add_header("Access-Control-Allow-Origin", "*")
    response_headers.add_header("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS")
    response_headers.add_header("Access-Control-Allow-Headers", "X-Requested-With, content-type, accept, mez-domain, tenant, client-id")
    response_headers["Content-Type"] = HTTP_RESPONSE_CONTENT_TYPE
    return response_headers


import json
def set_response(code, payload, response):
    set_options_header(response.headers)
    response.status_int = code

    if not isinstance(payload, dict):
        payload = {'text' : payload}
    json_response = payload

    response.out.write(json.dumps(json_response))
    return response