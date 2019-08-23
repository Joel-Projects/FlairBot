import os
import json


def get_secret(service, token='null'):
    secrets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    with open(f"{secrets_path}/secrets.json") as data:
        s = json.load(data)
        print(s)
        if token == 'null':
            secret = s[f'{service}']
        else:
            secret = s[f'{service}'][f'{token}']
        # logger.debug("EXIT secrets: {}".format(len(secret)))
    return secret