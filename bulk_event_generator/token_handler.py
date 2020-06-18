"""
 This file provide token in order to get access in MCP
"""
import requests


class TokenHandler(object):

    GET_TOKEN_URL = 'https://{}/tron/api/v1/tokens'
    GET_TOKEN_DATA = {'username': 'admin', 'password': 'adminpw', 'tenant': 'master', 'grant_type': 'password'}

    def __init__(self, ip_server):
        #  Get Token functionality
        self.active_token_url = self.GET_TOKEN_URL.format(ip_server)

        header_info = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.active_token = \
            requests.post(self.active_token_url, data=self.GET_TOKEN_DATA, headers=header_info, verify=False).json()[
                'token']

        self.active_header = {'Authorization': "Bearer " + self.active_token, 'Content-Type': 'application/json'}
        self.active_ip = ip_server

        print "active ip", self.active_ip, " active token ", self.active_token
