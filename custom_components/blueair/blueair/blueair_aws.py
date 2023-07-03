"""This module provides the Blueair class to communicate with the Blueair API on AWS."""


import logging
from typing import Any, Dict, List
import requests
import time
# from urllib.parse import urlencode


logger = logging.getLogger(__name__)

BLUEAIR_TOKEN_EXPIRATION_SECONDS = 86400

BLUEAIR_AWS_APIKEYS = {
  'us': {
    'gigyaRegion': 'us1',
    'restApiId': 'on1keymlmh',
    'awsRegion': 'us-east-2',
    'apiKey': '3_-xUbbrIY8QCbHDWQs1tLXE-CZBQ50SGElcOY5hF1euE11wCoIlNbjMGAFQ6UwhMY',
  },
  'eu': {
    'gigyaRegion': 'eu1',
    'restApiId': 'hkgmr8v960',
    'awsRegion': 'eu-west-1',
    'apiKey': '3_qRseYzrUJl1VyxvSJANalu_kNgQ83swB1B9uzgms58--5w1ClVNmrFdsDnWVQQCl',
  },
}


class BlueAirAws(object):
    def __init__(
        self,
        username: str,
        password: str,
        region: str
    ) -> None:
        self.username = username
        self.password = password
        self.region = region

        self.gigya_region = BLUEAIR_AWS_APIKEYS[self.region]['gigyaRegion']
        self.aws_region = BLUEAIR_AWS_APIKEYS[self.region]['awsRegion']
        self.aws_rest_api_id = BLUEAIR_AWS_APIKEYS[self.region]['restApiId']
        self.aws_api_key = BLUEAIR_AWS_APIKEYS[self.region]['apiKey']
        self.api_dns_name = f"{self.aws_rest_api_id}.execute-api.{self.aws_region}.amazonaws.com"
        self.api_url_prefix = f"https://{self.api_dns_name}"

        self.token_expiration_time = 0

        self.login()
    

    def renew_token_if_expired(self) -> None:
        if time.time() > self.token_expiration_time:
            self.login

    def login(self) -> None:

        gigya_headers = {
            'Host': f'accounts.{self.gigya_region}.gigya.com',
            'User-Agent': 'Blueair/58 CFNetwork/1327.0.4 Darwin/21.2.0',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(
            url= f"https://accounts.{self.gigya_region}.gigya.com/accounts.login",
            headers = gigya_headers,
            data = {
                'apikey': self.aws_api_key,
                'loginID': self.username,
                'password': self.password,
                'targetEnv': 'mobile',
            }
        ).json()

        logger.debug(f"Login response: {response}")

        session_token = response['sessionInfo']['sessionToken']
        session_secret = response['sessionInfo']['sessionSecret']

        # Get JWT Token
        response = requests.post(
            url = f"https://accounts.{self.gigya_region}.gigya.com/accounts.getJWT",
            headers = gigya_headers,
            data = {
                'oauth_token': session_token,
                'secret': session_secret,
                'targetEnv': 'mobile',
            }
        ).json()

        jwt_token = response['id_token']
        
        # Use JWT Token to get Access Token for Execute API endpoints
        response = requests.post(
            url = f"{self.api_url_prefix}/prod/c/login",
            headers = {
                'Host': self.api_dns_name,
                'Connection': 'keep-alive',
                'idtoken': jwt_token,
                'Accept': '*/*',
                'User-Agent': 'Blueair/58 CFNetwork/1327.0.4 Darwin/21.2.0',
                'Authorization': 'Bearer ' + jwt_token,
                'Accept-Language': 'en-US,en;q=0.9',
            },
        ).json()

        logger.debug(f"AWS Login response: {response}")

        self.access_token = response['access_token']
        self.token_expiration_time = time.time() + BLUEAIR_TOKEN_EXPIRATION_SECONDS

    def api_header(self) -> Dict[str, str]:
        return {
            'Host': self.api_dns_name,
            'Connection': 'keep-alive',
            'idtoken': self.access_token,
            'Accept': '*/*',
            'User-Agent': 'Blueair/58 CFNetwork/1327.0.4 Darwin/21.2.0',
            'Authorization': 'Bearer ' + self.access_token,
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_devices(self) -> List[Dict[str, Any]]:
        self.renew_token_if_expired()

        return requests.get(
            url = f"{self.api_url_prefix}/prod/c/registered-devices",
            headers = self.api_header()
        ).json()
    

    def get_info(self, device_name: str, device_uuid: str) -> Dict[str, Any]:
        self.renew_token_if_expired()
        
        return requests.post(
            url = f"{self.api_url_prefix}/prod/c/{device_name}/r/initial",
            headers= self.api_header() | {'Content-Type': 'application/json'},
            json = {
                'deviceconfigquery': [
                    {
                        'id': device_uuid,
                        'r': {
                            'r': [
                                'sensors',
                            ],
                        },
                    },
                ],
                'includestates': True,
                'eventsubscription': {
                    'include': [
                        {
                            'filter': {
                                'o': '= ' + device_uuid,
                            },
                        },
                    ],
                },
            }
        ).json()['deviceInfo'][0]
    

    def send_command(self, decvice_uuid: str, service: str, action_value: any):
        self.renew_token_if_expired()

        if type(action_value) == bool:
            value_key = 'vb'
        else:
            value_key = 'v'

        return requests.post(
            url = f"{self.api_url_prefix}/prod/c/{decvice_uuid}/a/{service}",
            headers= self.api_header() | {'Content-Type': 'application/json'},
            json = {
                'n': service,
                value_key: action_value,
            }
        ).json()
