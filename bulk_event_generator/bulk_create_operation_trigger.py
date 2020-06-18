"""
Load corresponding FRE and trigger operation creation in trigger on particular Resource
"""
import os
import json
import requests

from token_handler import TokenHandler

RESOURCE_ID = '5ee0ad05-4f52-4fae-885c-0fcd67d3a96d'

MCP_SERVER_IP = 'hac-prdubey-1'
PAYLOAD_DATA = 'data/notify_payload.json'
POST_OPERATION_ON_CONTAINER = 'https://{}/bpocore/market/api/v1/resources/{}/operations'


class CreateOperationTriggerExecutor(object):

    def __init__(self, ip_server,resource_id):
        self.token_handler = TokenHandler(ip_server)
        self.active_ip = ip_server
        self.resource_id = resource_id
        print ('Got Token')

    def load_payload_data(self):
        payload = read_json_contents(PAYLOAD_DATA)
        return payload

    def trigger_bulk_operation(self):
        print ('Bulk Operation Creation flow started ')
        payload = self.load_payload_data()
        print('Payload Data is : {}'.format(payload))

        url = POST_OPERATION_ON_CONTAINER.format(self.active_ip,self.resource_id)
        print('URL is : {}'.format(url))

        response = requests.post(url, json=payload, headers=self.token_handler.active_header, timeout=100.00, verify=False)
        response.raise_for_status()
        response.close()
        operation = response.json()
        print('created Operation id is :'+response.json()['id'])
        append_data_in_file('data/batch_run_data.txt', response.json()['id'])
        print('Operation Created' + "{}".format(json.dumps(operation)))


def main():
    executor = CreateOperationTriggerExecutor(MCP_SERVER_IP, RESOURCE_ID)
    executor.trigger_bulk_operation()


def read_json_contents(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    return data


def append_data_in_file(filename, operation_id):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, "a") as batch_file:
        batch_file.write(operation_id+"\n")
        batch_file.close()

if __name__ == "__main__":
    main()