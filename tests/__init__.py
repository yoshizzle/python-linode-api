from linode import LinodeClient

token = None

with open('tests/config') as config:
    token = config.read().strip()

def get_test_client():
    return LinodeClient(token)
