# Written for Python 3

# Disclaimer: Use this software at your own risk! Make sure your Passiv account is configured in a way that suits you.
# This script will ONLY list and execute available orders at your discretion. It is equivalent to logging in and clicking the Place Orders button.
# All orders are calculated on the server according to your account settings.

import requests
import urllib.request
import pyotp
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Account Variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TFA_SECRET = os.getenv("TFA_SECRET")

# API Variables
API_URL = "https://api.passiv.com/api/v1/"
AUTH_ENDPOINT = "auth/login"
PORTFOLIO_GROUP_ENDPOINT = "portfolioGroups/"
PG_INFO_ENDPOINT = 'portfolioGroups/<id>/info'
IMPACT_ENDPOINT = 'portfolioGroups/<pgid>/calculatedtrades/<ctid>/impact'
PLACE_ORDERS_ENDPOINT = 'portfolioGroups/<pgid>/calculatedtrades/<ctid>/placeOrders'

# Sign in
print("Signing in...")

if EMAIL == None:
    EMAIL = input("Email: ")
if (PASSWORD == None):
    PASSWORD = input("Password: ")

session = requests.session()
login_response = session.post(API_URL + AUTH_ENDPOINT, data={'email': EMAIL, 'password': PASSWORD})
login_response_json = login_response.json()

jwt_header = {}
tfa_code = ''
if 'mfa_required' in login_response_json:
    if login_response_json['mfa_required']['type'] == 'OTP_TOKEN' and TFA_SECRET != None:
        print("Generating and submitting TFA code...")
        tfa_code = pyotp.TOTP(TFA_SECRET).now()
    else:
        tfa_code = int(input("Enter your 2FA code: "))
    tfa_response = session.put(API_URL + AUTH_ENDPOINT, data={'remember_device': False, 'state': login_response_json['mfa_required']['state'], 'token': tfa_code})
    jwt_header = {'Authorization': 'JWT '+tfa_response.json()['token']}
else:
    if 'token' in login_response_json:
        jwt_header = {'Authorization': 'JWT '+login_response_json.json()['token']}

if jwt_header == {}:
    sys.exit('Login failed! Please try again.')

print("Success!")
print("Fetching available orders...")

portfolio_groups_response = session.get(API_URL + "portfolioGroups/", headers=jwt_header)
groups = portfolio_groups_response.json()

for group in groups:
    group_info = session.get(API_URL + PG_INFO_ENDPOINT.replace('<id>', group['id']), headers=jwt_header).json()
    print(group['name']+':')
    if 'calculated_trades' in group_info:
        calculated_trades = group_info['calculated_trades']

        if len(calculated_trades['trades']) == 0:
            print(" (none)")
            continue

        for trade in calculated_trades['trades']:
            print(' - '+trade['action']+" "+str(trade['units'])+" "+trade['universal_symbol']['symbol']+" @ $"+str(trade['price'])+str(trade['universal_symbol']['currency']['code']))

        impact = session.get(API_URL + IMPACT_ENDPOINT.replace('<pgid>', group['id']).replace('<ctid>', calculated_trades['id']), headers=jwt_header).json()
        if 'detail' in impact:
            print(impact['detail'])
        else:
            argument_allows = len(sys.argv) >= 2 and sys.argv[1] == '-y'
            user_allows = 'y' if argument_allows else input("Execute orders for "+group['name']+"? (y/n): ")
            if argument_allows or user_allows == 'y':
                placedOrders = session.post(API_URL + PLACE_ORDERS_ENDPOINT.replace('<pgid>', group['id']).replace('<ctid>', calculated_trades['id']), headers=jwt_header).json()
                if 'detail' in placedOrders:
                    print(placedOrders['detail'])
                else:
                    print('Orders executed!')