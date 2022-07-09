#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
import time

from lib import *

config = {}
ipam4_old = {}


def main():
    get_config()

    if not config['one_shot']:
        while True:
            loop()
            time.sleep(config['refresh_interval'])

    loop()


def loop():
    container.init(config)
    ipam4 = container.generate_container_list()
    global ipam4_old

    additions4 = determine_additions(ipam4, ipam4_old)
    deletions4 = determine_deletions(ipam4, ipam4_old)

    nsupdate.init(config)
    nsupdate.delete_records(deletions4)
    nsupdate.add_records(additions4)

    ipam4_old = ipam4


def get_config():
    config_file = sys.argv[1] if len(sys.argv) >= 2 else 'config'
    load_dotenv(config_file)

    config['domain'] = os.environ.get("DOMAIN")
    config['hostname_label'] = os.environ.get("HOSTNAME_LABEL")
    config['default_network'] = os.environ.get("DEFAULT_NETWORK")
    config['refresh_interval'] = int(os.environ.get("REFRESH_INTERVAL"))
    config['one_shot'] = os.environ.get("ONE_SHOT").lower() in ['true', 'yes']
    config['nameserver'] = os.environ.get("NAMESERVER")
    config['tsig_name'] = os.environ.get("TSIG_NAME")
    config['tsig_key'] = os.environ.get("TSIG_KEY")


def determine_additions(ipam, ipam_old):
    return {k: v for k, v in ipam.items() if k not in ipam_old}


def determine_deletions(ipam, ipam_old):
    return {k: v for k, v in ipam_old.items() if k not in ipam}
    pass


if __name__ == "__main__":
    main()
